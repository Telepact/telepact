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
import contextvars
import json
from pathlib import Path
import sys
import time
from typing import Any

import nats
from nats.aio.msg import Msg
from telepact import Client, FunctionRouter, Message, Server, TelepactSchema

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "gen" / "py"))
import benchmark_pb2  # type: ignore  # noqa: E402

from common import load_json, unique_run_id, write_json

BENCHMARK_HEADER = "x-benchmark-id"


def _now_ns() -> int:
    return time.perf_counter_ns()


def _payload_value(payload: dict[str, Any]) -> tuple[str, Any]:
    return next(iter(payload.items()))


class ProtobufCodec:
    @staticmethod
    def _item_to_proto(target: Any, value: dict[str, Any]) -> None:
        for key, field_value in value.items():
            setattr(target, key, field_value)

    @classmethod
    def _payload_to_proto(cls, payload: dict[str, Any]) -> benchmark_pb2.Payload:
        message = benchmark_pb2.Payload()
        variant, value = _payload_value(payload)
        if variant == "TypicalSingle":
            cls._item_to_proto(message.typical_single, value)
        elif variant == "TypicalList":
            for item in value["items"]:
                cls._item_to_proto(message.typical_list.items.add(), item)
        elif variant == "StringSingle":
            cls._item_to_proto(message.string_single, value)
        elif variant == "StringList":
            for item in value["items"]:
                cls._item_to_proto(message.string_list.items.add(), item)
        elif variant == "NumberSingle":
            cls._item_to_proto(message.number_single, value)
        elif variant == "NumberList":
            for item in value["items"]:
                cls._item_to_proto(message.number_list.items.add(), item)
        else:
            raise ValueError(f"unknown payload variant: {variant}")
        return message

    @classmethod
    def encode_request(cls, request: dict[str, Any]) -> bytes:
        message = benchmark_pb2.RoundTripRequest(
            scenario=request["scenario"],
            payload=cls._payload_to_proto(request["payload"]),
        )
        return message.SerializeToString()

    @classmethod
    def encode_response(cls, response: dict[str, Any]) -> bytes:
        message = benchmark_pb2.RoundTripResponse(
            scenario=response["scenario"],
            payload=cls._payload_to_proto(response["payload"]),
        )
        return message.SerializeToString()

    @staticmethod
    def _item_from_proto(message: Any) -> dict[str, Any]:
        return {field.name: getattr(message, field.name) for field in message.DESCRIPTOR.fields}

    @classmethod
    def _payload_from_proto(cls, payload: benchmark_pb2.Payload) -> dict[str, Any]:
        which = payload.WhichOneof("value")
        if which is None:
            raise ValueError("payload missing oneof value")
        value = getattr(payload, which)
        if which.endswith("_list"):
            items = [cls._item_from_proto(item) for item in value.items]
            if which == "typical_list":
                return {"TypicalList": {"items": items}}
            if which == "string_list":
                return {"StringList": {"items": items}}
            return {"NumberList": {"items": items}}
        item = cls._item_from_proto(value)
        if which == "typical_single":
            return {"TypicalSingle": item}
        if which == "string_single":
            return {"StringSingle": item}
        return {"NumberSingle": item}

    @classmethod
    def decode_request(cls, payload: bytes) -> dict[str, Any]:
        message = benchmark_pb2.RoundTripRequest()
        message.ParseFromString(payload)
        return {"scenario": message.scenario, "payload": cls._payload_from_proto(message.payload)}

    @classmethod
    def decode_response(cls, payload: bytes) -> dict[str, Any]:
        message = benchmark_pb2.RoundTripResponse()
        message.ParseFromString(payload)
        return {"scenario": message.scenario, "payload": cls._payload_from_proto(message.payload)}


class TelepactBenchClient:
    def __init__(self, connection: nats.NATS, subject: str, *, use_binary: bool, packed: bool, state: dict[str, dict[str, Any]]):
        self.connection = connection
        self.subject = subject
        self.packed = packed
        self.state = state
        options = Client.Options()
        options.use_binary = use_binary
        options.always_send_json = not use_binary
        self.client = Client(self._adapter, options)

    async def _adapter(self, message: Message, serializer: Any) -> Message:
        benchmark_id = unique_run_id()
        sample = self.state[benchmark_id]
        headers = {BENCHMARK_HEADER: benchmark_id}
        request_started = _now_ns()
        request_bytes = serializer.serialize(message)
        sample["client_request_serialize_ns"] = _now_ns() - request_started
        sample["request_size_bytes"] = len(request_bytes)
        sample["client_request_sent_ns"] = _now_ns()
        response_message = await self.connection.request(self.subject, request_bytes, timeout=30, headers=headers)
        sample["client_response_received_ns"] = _now_ns()
        response_bytes = response_message.data
        sample["response_size_bytes"] = len(response_bytes)
        response_started = _now_ns()
        deserialized = serializer.deserialize(response_bytes)
        sample["client_response_deserialize_ns"] = _now_ns() - response_started
        server_state = self.state.pop(benchmark_id)
        sample["request_network_transit_ns"] = server_state["server_request_received_ns"] - sample["client_request_sent_ns"]
        sample["response_network_transit_ns"] = sample["client_response_received_ns"] - server_state["server_response_sent_ns"]
        sample["server_request_deserialize_ns"] = server_state["server_request_deserialize_ns"]
        sample["server_response_serialize_ns"] = server_state["server_response_serialize_ns"]
        return deserialized

    async def round_trip(self, request: dict[str, Any]) -> None:
        headers: dict[str, Any] = {}
        if self.packed:
            headers["@pac_"] = True
        response = await self.client.request(Message(headers, {"fn.roundTrip": request}))
        assert response.body["Ok_"] == request


async def _build_telepact_server(schema_dir: Path, state: dict[str, dict[str, Any]]) -> Server:
    current_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("current_benchmark_id", default=None)

    async def round_trip(function_name: str, request_message: Message) -> Message:
        return Message({}, {"Ok_": request_message.body[function_name]})

    options = Server.Options()
    options.auth_required = False

    def on_request(_message: Message) -> None:
        benchmark_id = current_id.get()
        if benchmark_id is None:
            return
        state[benchmark_id]["server_request_deserialize_ns"] = _now_ns() - state[benchmark_id]["server_request_received_ns"]

    def on_response(_message: Message) -> None:
        benchmark_id = current_id.get()
        if benchmark_id is None:
            return
        state[benchmark_id]["server_response_ready_ns"] = _now_ns()

    options.on_request = on_request
    options.on_response = on_response
    schema = TelepactSchema.from_directory(str(schema_dir))
    server = Server(schema, FunctionRouter({"fn.roundTrip": round_trip}), options)
    server._benchmark_context = current_id  # type: ignore[attr-defined]
    return server


async def _run_plain_json(connection: nats.NATS, subject: str, request: dict[str, Any], state: dict[str, dict[str, Any]]) -> dict[str, Any]:
    benchmark_id = unique_run_id()
    sample = state[benchmark_id]
    request_started = _now_ns()
    request_bytes = json.dumps(request, separators=(",", ":")).encode()
    sample["client_request_serialize_ns"] = _now_ns() - request_started
    sample["request_size_bytes"] = len(request_bytes)
    sample["client_request_sent_ns"] = _now_ns()
    response = await connection.request(subject, request_bytes, timeout=30, headers={BENCHMARK_HEADER: benchmark_id})
    sample["client_response_received_ns"] = _now_ns()
    response_bytes = response.data
    sample["response_size_bytes"] = len(response_bytes)
    response_started = _now_ns()
    decoded = json.loads(response_bytes.decode())
    sample["client_response_deserialize_ns"] = _now_ns() - response_started
    server_state = state.pop(benchmark_id)
    sample["request_network_transit_ns"] = server_state["server_request_received_ns"] - sample["client_request_sent_ns"]
    sample["response_network_transit_ns"] = sample["client_response_received_ns"] - server_state["server_response_sent_ns"]
    sample["server_request_deserialize_ns"] = server_state["server_request_deserialize_ns"]
    sample["server_response_serialize_ns"] = server_state["server_response_serialize_ns"]
    return decoded


async def _run_protobuf(connection: nats.NATS, subject: str, request: dict[str, Any], state: dict[str, dict[str, Any]]) -> dict[str, Any]:
    benchmark_id = unique_run_id()
    sample = state[benchmark_id]
    request_started = _now_ns()
    request_bytes = ProtobufCodec.encode_request(request)
    sample["client_request_serialize_ns"] = _now_ns() - request_started
    sample["request_size_bytes"] = len(request_bytes)
    sample["client_request_sent_ns"] = _now_ns()
    response = await connection.request(subject, request_bytes, timeout=30, headers={BENCHMARK_HEADER: benchmark_id})
    sample["client_response_received_ns"] = _now_ns()
    response_bytes = response.data
    sample["response_size_bytes"] = len(response_bytes)
    response_started = _now_ns()
    decoded = ProtobufCodec.decode_response(response_bytes)
    sample["client_response_deserialize_ns"] = _now_ns() - response_started
    server_state = state.pop(benchmark_id)
    sample["request_network_transit_ns"] = server_state["server_request_received_ns"] - sample["client_request_sent_ns"]
    sample["response_network_transit_ns"] = sample["client_response_received_ns"] - server_state["server_response_sent_ns"]
    sample["server_request_deserialize_ns"] = server_state["server_request_deserialize_ns"]
    sample["server_response_serialize_ns"] = server_state["server_response_serialize_ns"]
    return decoded


async def _benchmark(args: argparse.Namespace) -> list[dict[str, Any]]:
    manifest = load_json(Path(args.manifest))
    schema_dir = Path(args.schema_dir)
    state: dict[str, dict[str, Any]] = {}
    connection = await nats.connect(args.nats_url)
    server = await _build_telepact_server(schema_dir, state)
    current_id = server._benchmark_context  # type: ignore[attr-defined]
    subject_prefix = f"telepact.performance.{args.language}.{args.latency}.{unique_run_id()}"
    telepact_subject = f"{subject_prefix}.telepact"
    protobuf_subject = f"{subject_prefix}.protobuf"
    json_subject = f"{subject_prefix}.json"

    async def telepact_handler(msg: Msg) -> None:
        benchmark_id = msg.headers[BENCHMARK_HEADER]
        state[benchmark_id]["server_request_received_ns"] = _now_ns()
        token = current_id.set(benchmark_id)
        try:
            response = await server.process(msg.data)
        finally:
            current_id.reset(token)
        state[benchmark_id]["server_response_serialize_ns"] = _now_ns() - state[benchmark_id]["server_response_ready_ns"]
        state[benchmark_id]["server_response_sent_ns"] = _now_ns()
        await connection.publish(msg.reply, response.bytes)

    async def protobuf_handler(msg: Msg) -> None:
        benchmark_id = msg.headers[BENCHMARK_HEADER]
        sample = state[benchmark_id]
        sample["server_request_received_ns"] = _now_ns()
        request_started = _now_ns()
        request = ProtobufCodec.decode_request(msg.data)
        sample["server_request_deserialize_ns"] = _now_ns() - request_started
        response_started = _now_ns()
        response_bytes = ProtobufCodec.encode_response(request)
        sample["server_response_serialize_ns"] = _now_ns() - response_started
        sample["server_response_sent_ns"] = _now_ns()
        await connection.publish(msg.reply, response_bytes)

    async def json_handler(msg: Msg) -> None:
        benchmark_id = msg.headers[BENCHMARK_HEADER]
        sample = state[benchmark_id]
        sample["server_request_received_ns"] = _now_ns()
        request_started = _now_ns()
        request = json.loads(msg.data.decode())
        sample["server_request_deserialize_ns"] = _now_ns() - request_started
        response_started = _now_ns()
        response_bytes = json.dumps(request, separators=(",", ":")).encode()
        sample["server_response_serialize_ns"] = _now_ns() - response_started
        sample["server_response_sent_ns"] = _now_ns()
        await connection.publish(msg.reply, response_bytes)

    subscriptions = [
        await connection.subscribe(telepact_subject, cb=telepact_handler),
        await connection.subscribe(protobuf_subject, cb=protobuf_handler),
        await connection.subscribe(json_subject, cb=json_handler),
    ]
    await connection.flush()

    telepact_json_client = TelepactBenchClient(connection, telepact_subject, use_binary=False, packed=False, state=state)
    telepact_binary_client = TelepactBenchClient(connection, telepact_subject, use_binary=True, packed=False, state=state)
    telepact_packed_client = TelepactBenchClient(connection, telepact_subject, use_binary=True, packed=True, state=state)

    samples: list[dict[str, Any]] = []
    warmup_iterations = int(manifest["warmupIterations"])
    measure_iterations = int(manifest["measureIterations"])

    for scenario in manifest["scenarios"]:
        request = scenario["request"]
        for _ in range(warmup_iterations):
            await telepact_json_client.round_trip(request)
            await telepact_binary_client.round_trip(request)
            await telepact_packed_client.round_trip(request)
            assert await _run_protobuf(connection, protobuf_subject, request, {unique_run_id(): {}}) == request
            assert await _run_plain_json(connection, json_subject, request, {unique_run_id(): {}}) == request

        for method in manifest["methods"]:
            for iteration in range(measure_iterations):
                sample = {
                    "language": args.language,
                    "latency": args.latency,
                    "method": method,
                    "scenario": scenario["name"],
                    "collection_shape": scenario["collectionShape"],
                    "data_shape": scenario["dataShape"],
                    "iteration": iteration,
                }
                benchmark_id = unique_run_id()
                state[benchmark_id] = sample
                if method == "telepact_json":
                    telepact_json_client.state[benchmark_id] = sample
                    await telepact_json_client.round_trip(request)
                elif method == "telepact_binary":
                    telepact_binary_client.state[benchmark_id] = sample
                    await telepact_binary_client.round_trip(request)
                elif method == "telepact_packed_binary":
                    telepact_packed_client.state[benchmark_id] = sample
                    await telepact_packed_client.round_trip(request)
                elif method == "protobuf":
                    result = await _run_protobuf(connection, protobuf_subject, request, {benchmark_id: sample})
                    assert result == request
                else:
                    result = await _run_plain_json(connection, json_subject, request, {benchmark_id: sample})
                    assert result == request
                samples.append(sample)

    for subscription in subscriptions:
        await subscription.unsubscribe()
    await connection.drain()
    return samples


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", default="python")
    parser.add_argument("--latency", required=True)
    parser.add_argument("--nats-url", required=True)
    parser.add_argument("--schema-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    samples = asyncio.run(_benchmark(args))
    write_json(Path(args.output), samples)


if __name__ == "__main__":
    main()
