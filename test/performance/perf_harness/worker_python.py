#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import time
import uuid
from typing import Any, Awaitable, Callable

import nats
from nats.errors import TimeoutError as NatsTimeoutError
from telepact import Client, FunctionRouter, Message, Server, TelepactSchema

from . import benchmark_pb2
from .common import (
    FUNCTION_NAMES,
    NATS_REQUEST_TIMEOUT_SECONDS,
    NATS_TIMEOUT_ADDITIONAL_RETRIES,
    NATS_TIMEOUT_RETRY_DELAY_SECONDS,
    PLAIN_FUNCTION_NAMES,
    PROTODESC,
    SCHEMA_DIR,
    Scenario,
    iter_scenarios,
    load_payloads,
    scenario_record,
    utc_now_iso,
    write_json,
)


class RetryingNatsClient:
    def __init__(self, client: nats.aio.client.Client):
        self._client = client

    async def request(self, subject: str, payload: bytes, timeout: float) -> nats.aio.msg.Msg:
        for attempt in range(NATS_TIMEOUT_ADDITIONAL_RETRIES + 1):
            try:
                return await self._client.request(subject, payload, timeout=timeout)
            except NatsTimeoutError:
                if attempt >= NATS_TIMEOUT_ADDITIONAL_RETRIES:
                    raise
                await asyncio.sleep(NATS_TIMEOUT_RETRY_DELAY_SECONDS)
        raise RuntimeError("unreachable")


async def connect_client(url: str) -> RetryingNatsClient:
    client = await nats.connect(url)
    return RetryingNatsClient(client)


class PythonWorker:
    def __init__(self, local_nats_url: str, remote_nats_url: str, iterations: int, warmup_iterations: int):
        self.local_nats_url = local_nats_url
        self.remote_nats_url = remote_nats_url
        self.iterations = iterations
        self.warmup_iterations = warmup_iterations
        self.payloads = load_payloads()

    async def run(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for network_latency, nats_url in (("close", self.local_nats_url), ("far", self.remote_nats_url)):
            client = await connect_client(nats_url)
            server = await nats.connect(nats_url)
            try:
                for scenario in iter_scenarios():
                    if scenario.network_latency != network_latency:
                        continue
                    samples = await self.run_scenario(client, server, scenario)
                    results.append(scenario_record("python", scenario, self.iterations, self.warmup_iterations, samples))
            finally:
                await client._client.close()
                await server.close()
        return results

    async def run_scenario(self, client: RetryingNatsClient, server: nats.aio.client.Client, scenario: Scenario) -> list[dict[str, Any]]:
        subject = f"perf.python.{uuid.uuid4().hex}"
        queue: asyncio.Queue[dict[str, int]] = asyncio.Queue()
        payload = self.payloads[scenario.data_shape][scenario.collection_shape]

        if scenario.method.startswith("telepact"):
            subscription, request_once = await self._create_telepact_runner(server, client, subject, scenario, queue)
        elif scenario.method == "protobuf":
            subscription, request_once = await self._create_protobuf_runner(server, client, subject, scenario, queue)
        else:
            subscription, request_once = await self._create_plain_json_runner(server, client, subject, scenario, queue)

        try:
            for _ in range(self.warmup_iterations):
                await request_once(payload)
            samples: list[dict[str, Any]] = []
            for _ in range(self.iterations):
                samples.append(await request_once(payload))
            return samples
        finally:
            await subscription.unsubscribe()

    async def _create_plain_json_runner(self, server: nats.aio.client.Client, client: RetryingNatsClient, subject: str, scenario: Scenario, queue: asyncio.Queue[dict[str, int]]):
        async def handler(msg: nats.aio.msg.Msg) -> None:
            received_at = time.perf_counter_ns()
            request = json.loads(msg.data)
            after_deserialize = time.perf_counter_ns()
            response_object = {
                "function": request["function"],
                "items": request["items"],
            }
            before_serialize = time.perf_counter_ns()
            response_bytes = json.dumps(response_object, separators=(",", ":")).encode()
            response_sent_at = time.perf_counter_ns()
            queue.put_nowait({
                "requestNetworkArrivalNs": received_at,
                "serverRequestDeserializationTimeNs": after_deserialize - received_at,
                "serverResponseSerializationTimeNs": response_sent_at - before_serialize,
                "responseSentAtNs": response_sent_at,
            })
            await server.publish(msg.reply, response_bytes)

        sub = await server.subscribe(subject, cb=handler)
        await server.flush()

        async def request_once(payload: list[dict[str, Any]]) -> dict[str, Any]:
            request_object = {
                "function": PLAIN_FUNCTION_NAMES[scenario.data_shape],
                "items": payload,
            }
            serialize_start = time.perf_counter_ns()
            request_bytes = json.dumps(request_object, separators=(",", ":")).encode()
            serialize_end = time.perf_counter_ns()
            sent_at = time.perf_counter_ns()
            response = await client.request(subject, request_bytes, timeout=NATS_REQUEST_TIMEOUT_SECONDS)
            received_at = time.perf_counter_ns()
            deserialize_start = time.perf_counter_ns()
            response_object = json.loads(response.data)
            deserialize_end = time.perf_counter_ns()
            assert response_object["items"] == payload
            server_metrics = await queue.get()
            return {
                "clientRequestSerializationTimeNs": serialize_end - serialize_start,
                "serializedRequestSizeBytes": len(request_bytes),
                "requestNetworkTransitTimeNs": server_metrics["requestNetworkArrivalNs"] - sent_at,
                "serverRequestDeserializationTimeNs": server_metrics["serverRequestDeserializationTimeNs"],
                "serverResponseSerializationTimeNs": server_metrics["serverResponseSerializationTimeNs"],
                "serializedResponseSizeBytes": len(response.data),
                "responseNetworkTransitTimeNs": received_at - server_metrics["responseSentAtNs"],
                "clientResponseDeserializationTimeNs": deserialize_end - deserialize_start,
            }

        return sub, request_once

    async def _create_protobuf_runner(self, server: nats.aio.client.Client, client: RetryingNatsClient, subject: str, scenario: Scenario, queue: asyncio.Queue[dict[str, int]]):
        request_type_name, response_type_name, field_name = PROTODESC[scenario.data_shape]
        request_type = getattr(benchmark_pb2, request_type_name)
        response_type = getattr(benchmark_pb2, response_type_name)
        item_descriptor = request_type.DESCRIPTOR.fields_by_name[field_name].message_type
        item_type = getattr(benchmark_pb2, item_descriptor.name)

        def build_request(payload: list[dict[str, Any]]):
            message = request_type()
            repeated = getattr(message, field_name)
            repeated.extend(item_type(**item) for item in payload)
            return message

        async def handler(msg: nats.aio.msg.Msg) -> None:
            received_at = time.perf_counter_ns()
            request = request_type()
            request.ParseFromString(msg.data)
            after_deserialize = time.perf_counter_ns()
            response = response_type()
            getattr(response, field_name).extend(getattr(request, field_name))
            before_serialize = time.perf_counter_ns()
            response_bytes = response.SerializeToString()
            response_sent_at = time.perf_counter_ns()
            queue.put_nowait({
                "requestNetworkArrivalNs": received_at,
                "serverRequestDeserializationTimeNs": after_deserialize - received_at,
                "serverResponseSerializationTimeNs": response_sent_at - before_serialize,
                "responseSentAtNs": response_sent_at,
            })
            await server.publish(msg.reply, response_bytes)

        sub = await server.subscribe(subject, cb=handler)
        await server.flush()

        async def request_once(payload: list[dict[str, Any]]) -> dict[str, Any]:
            request_message = build_request(payload)
            serialize_start = time.perf_counter_ns()
            request_bytes = request_message.SerializeToString()
            serialize_end = time.perf_counter_ns()
            sent_at = time.perf_counter_ns()
            response = await client.request(subject, request_bytes, timeout=NATS_REQUEST_TIMEOUT_SECONDS)
            received_at = time.perf_counter_ns()
            deserialize_start = time.perf_counter_ns()
            response_message = response_type()
            response_message.ParseFromString(response.data)
            deserialize_end = time.perf_counter_ns()
            assert len(getattr(response_message, field_name)) == len(payload)
            server_metrics = await queue.get()
            return {
                "clientRequestSerializationTimeNs": serialize_end - serialize_start,
                "serializedRequestSizeBytes": len(request_bytes),
                "requestNetworkTransitTimeNs": server_metrics["requestNetworkArrivalNs"] - sent_at,
                "serverRequestDeserializationTimeNs": server_metrics["serverRequestDeserializationTimeNs"],
                "serverResponseSerializationTimeNs": server_metrics["serverResponseSerializationTimeNs"],
                "serializedResponseSizeBytes": len(response.data),
                "responseNetworkTransitTimeNs": received_at - server_metrics["responseSentAtNs"],
                "clientResponseDeserializationTimeNs": deserialize_end - deserialize_start,
            }

        return sub, request_once

    async def _create_telepact_runner(self, server_connection: nats.aio.client.Client, client_connection: RetryingNatsClient, subject: str, scenario: Scenario, queue: asyncio.Queue[dict[str, int]]):
        schema = TelepactSchema.from_directory(str(SCHEMA_DIR))
        function_name = FUNCTION_NAMES[scenario.data_shape]

        async def echo_route(function_name_unused: str, request_message: Message) -> Message:
            return Message({}, {"Ok_": {"items": request_message.body[function_name_unused]["items"]}})

        server_state: dict[str, int] = {}
        function_router = FunctionRouter({
            "fn.roundTripTypical": echo_route,
            "fn.roundTripStrings": echo_route,
            "fn.roundTripNumbers": echo_route,
        })
        options = Server.Options()
        options.auth_required = False
        options.on_request = lambda _message: server_state.__setitem__("afterDeserializeNs", time.perf_counter_ns())
        options.on_response = lambda _message: server_state.__setitem__("beforeSerializeNs", time.perf_counter_ns())
        server = Server(schema, function_router, options)

        async def handler(msg: nats.aio.msg.Msg) -> None:
            received_at = time.perf_counter_ns()
            server_state.clear()
            response = await server.process(msg.data)
            response_sent_at = time.perf_counter_ns()
            queue.put_nowait({
                "requestNetworkArrivalNs": received_at,
                "serverRequestDeserializationTimeNs": server_state["afterDeserializeNs"] - received_at,
                "serverResponseSerializationTimeNs": response_sent_at - server_state["beforeSerializeNs"],
                "responseSentAtNs": response_sent_at,
            })
            await server_connection.publish(msg.reply, response.bytes)

        sub = await server_connection.subscribe(subject, cb=handler)
        await server_connection.flush()

        async def adapter(message: Message, serializer) -> Message:
            serialize_start = time.perf_counter_ns()
            request_bytes = serializer.serialize(message)
            serialize_end = time.perf_counter_ns()
            sent_at = time.perf_counter_ns()
            response_msg = await client_connection.request(subject, request_bytes, timeout=NATS_REQUEST_TIMEOUT_SECONDS)
            received_at = time.perf_counter_ns()
            deserialize_start = time.perf_counter_ns()
            response_message = serializer.deserialize(response_msg.data)
            deserialize_end = time.perf_counter_ns()
            server_metrics = await queue.get()
            adapter.last_sample = {
                "clientRequestSerializationTimeNs": serialize_end - serialize_start,
                "serializedRequestSizeBytes": len(request_bytes),
                "requestNetworkTransitTimeNs": server_metrics["requestNetworkArrivalNs"] - sent_at,
                "serverRequestDeserializationTimeNs": server_metrics["serverRequestDeserializationTimeNs"],
                "serverResponseSerializationTimeNs": server_metrics["serverResponseSerializationTimeNs"],
                "serializedResponseSizeBytes": len(response_msg.data),
                "responseNetworkTransitTimeNs": received_at - server_metrics["responseSentAtNs"],
                "clientResponseDeserializationTimeNs": deserialize_end - deserialize_start,
            }
            return response_message

        adapter.last_sample = {}
        client_options = Client.Options()
        client_options.use_binary = scenario.method != "telepact-json"
        client_options.always_send_json = scenario.method == "telepact-json"
        client = Client(adapter, client_options)

        async def request_once(payload: list[dict[str, Any]]) -> dict[str, Any]:
            headers = {"@pac_": True} if scenario.method == "telepact-packed-binary" else {}
            response = await client.request(Message(headers, {function_name: {"items": payload}}))
            assert response.body["Ok_"]["items"] == payload
            return dict(adapter.last_sample)

        return sub, request_once


async def async_main(args: argparse.Namespace) -> None:
    worker = PythonWorker(args.local_nats_url, args.remote_nats_url, args.iterations, args.warmup_iterations)
    results = await worker.run()
    write_json(Path(args.output), {
        "metadata": {
            "language": "python",
            "generatedAt": utc_now_iso(),
            "iterations": args.iterations,
            "warmupIterations": args.warmup_iterations,
            "localNatsUrl": args.local_nats_url,
            "remoteNatsUrl": args.remote_nats_url,
        },
        "scenarios": results,
    })


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, required=True)
    parser.add_argument("--warmup-iterations", type=int, required=True)
    parser.add_argument("--local-nats-url", required=True)
    parser.add_argument("--remote-nats-url", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    asyncio.run(async_main(parse_args()))


if __name__ == "__main__":
    main()
