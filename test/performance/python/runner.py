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
import base64
import copy
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import nats
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory
from telepact import Client, FunctionRouter, Message, Server, TelepactSchema


def now_ns() -> int:
    return time.perf_counter_ns()


def ns_to_ms(duration_ns: int) -> float:
    return duration_ns / 1_000_000


@dataclass
class Sample:
    request_serialization_ms: float = 0.0
    request_size_bytes: int = 0
    request_network_transit_ms: float = 0.0
    server_request_deserialization_ms: float = 0.0
    server_response_serialization_ms: float = 0.0
    response_size_bytes: int = 0
    response_network_transit_ms: float = 0.0
    response_deserialization_ms: float = 0.0

    def as_dict(self) -> dict[str, float | int]:
        return {
            "request_serialization_ms": self.request_serialization_ms,
            "request_size_bytes": self.request_size_bytes,
            "request_network_transit_ms": self.request_network_transit_ms,
            "server_request_deserialization_ms": self.server_request_deserialization_ms,
            "server_response_serialization_ms": self.server_response_serialization_ms,
            "response_size_bytes": self.response_size_bytes,
            "response_network_transit_ms": self.response_network_transit_ms,
            "response_deserialization_ms": self.response_deserialization_ms,
        }


class ProtobufCodec:
    def __init__(self, schema_dir: Path) -> None:
        descriptor_bytes = base64.b64decode((schema_dir / "protobuf" / "benchmark.desc.base64").read_text(encoding="utf-8"))
        file_set = descriptor_pb2.FileDescriptorSet()
        file_set.ParseFromString(descriptor_bytes)
        pool = descriptor_pool.DescriptorPool()
        for file_proto in file_set.file:
            pool.AddSerializedFile(file_proto.SerializeToString())

        request_descriptor = pool.FindMessageTypeByName("telepact.performance.EchoRequest")
        response_descriptor = pool.FindMessageTypeByName("telepact.performance.EchoResponse")
        self.request_class = message_factory.GetMessageClass(request_descriptor)
        self.response_class = message_factory.GetMessageClass(response_descriptor)

    def encode_request(self, payload: dict[str, Any]) -> bytes:
        return self._build_message(self.request_class(), payload).SerializeToString()

    def decode_request(self, payload_bytes: bytes) -> dict[str, Any]:
        message = self.request_class()
        message.ParseFromString(payload_bytes)
        return self._message_to_payload(message)

    def encode_response(self, payload: dict[str, Any]) -> bytes:
        return self._build_message(self.response_class(), payload).SerializeToString()

    def decode_response(self, payload_bytes: bytes) -> dict[str, Any]:
        message = self.response_class()
        message.ParseFromString(payload_bytes)
        return self._message_to_payload(message)

    def _build_message(self, message: Any, payload: dict[str, Any]) -> Any:
        for item in payload["items"]:
            entry = message.items.add()
            kind = item["kind"]
            data = item["data"]
            if kind == "typical":
                for key, value in data.items():
                    setattr(entry.typical, key, value)
            elif kind == "all_strings":
                for key, value in data.items():
                    setattr(entry.all_strings, key, value)
            elif kind == "all_numbers":
                for key, value in data.items():
                    setattr(entry.all_numbers, key, value)
            else:
                raise ValueError(f"unsupported kind: {kind}")
        return message

    def _message_to_payload(self, message: Any) -> dict[str, Any]:
        items: list[dict[str, Any]] = []
        for entry in message.items:
            if entry.HasField("typical"):
                items.append({"kind": "typical", "data": self._scalar_map(entry.typical)})
            elif entry.HasField("all_strings"):
                items.append({"kind": "all_strings", "data": self._scalar_map(entry.all_strings)})
            elif entry.HasField("all_numbers"):
                items.append({"kind": "all_numbers", "data": self._scalar_map(entry.all_numbers)})
            else:
                raise ValueError("protobuf item missing variant")
        return {"items": items}

    @staticmethod
    def _scalar_map(message: Any) -> dict[str, Any]:
        return {field.name: getattr(message, field.name) for field in message.DESCRIPTOR.fields}


class PlainJsonCodec:
    @staticmethod
    def encode(payload: dict[str, Any]) -> bytes:
        return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

    @staticmethod
    def decode(payload_bytes: bytes) -> dict[str, Any]:
        return json.loads(payload_bytes.decode("utf-8"))


def canonical_to_telepact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    tag_map = {
        "typical": "Typical",
        "all_strings": "AllStrings",
        "all_numbers": "AllNumbers",
    }
    return {
        "items": [
            {tag_map[item["kind"]]: copy.deepcopy(item["data"])}
            for item in payload["items"]
        ]
    }


class BenchmarkRunner:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        scenarios = json.loads(Path(args.payloads).read_text(encoding="utf-8"))
        self.payload = scenarios[args.collection_shape][args.data_shape]
        self.telepact_payload = canonical_to_telepact_payload(self.payload)
        schema_root = Path(args.schema_dir)
        self.telepact_schema = TelepactSchema.from_directory(str(schema_root / "telepact"))
        self.protobuf = ProtobufCodec(schema_root)
        self.nc = None
        self.subscription = None
        self.current_sample: Sample | None = None
        self.telepact_client: Client | None = None
        self.server_received_ns = 0
        self.server_reply_sent_ns = 0
        self.server_on_request_ns = 0
        self.server_on_response_ns = 0
        self.current_send_ns = 0
        self.last_request_was_binary = False
        self.last_response_was_binary = False
        self.server_response_payload = copy.deepcopy(self.telepact_payload)

    async def __aenter__(self) -> "BenchmarkRunner":
        self.nc = await nats.connect(self.args.nats_url)
        await self._start_server()
        if self.args.method.startswith("telepact"):
            self._start_telepact_client()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.subscription is not None:
            await self.subscription.unsubscribe()
        if self.nc is not None:
            await self.nc.close()

    async def _start_server(self) -> None:
        assert self.nc is not None

        if self.args.method.startswith("telepact"):
            options = Server.Options()
            options.auth_required = False
            options.on_request = self._telepact_on_request
            options.on_response = self._telepact_on_response
            server = Server(
                self.telepact_schema,
                FunctionRouter({"fn.echo": self._telepact_echo}),
                options,
            )

            async def handler(msg) -> None:
                self.server_received_ns = now_ns()
                response = await server.process(msg.data)
                response_ready_ns = now_ns()
                assert self.current_sample is not None
                self.current_sample.request_network_transit_ms = ns_to_ms(
                    self.server_received_ns - self.current_send_ns
                )
                self.current_sample.server_request_deserialization_ms = ns_to_ms(
                    self.server_on_request_ns - self.server_received_ns
                )
                self.current_sample.server_response_serialization_ms = ns_to_ms(
                    response_ready_ns - self.server_on_response_ns
                )
                self.current_sample.response_size_bytes = len(response.bytes)
                self.last_response_was_binary = response.bytes[0] == 0x92
                self.server_reply_sent_ns = now_ns()
                await self.nc.publish(msg.reply, response.bytes)

            self.subscription = await self.nc.subscribe(self.args.subject, cb=handler)
        elif self.args.method == "protobuf":
            async def handler(msg) -> None:
                self.server_received_ns = now_ns()
                request_decode_start = now_ns()
                decoded = self.protobuf.decode_request(msg.data)
                request_decode_end = now_ns()
                response_encode_start = now_ns()
                response_bytes = self.protobuf.encode_response(decoded)
                response_encode_end = now_ns()
                assert self.current_sample is not None
                self.current_sample.request_network_transit_ms = ns_to_ms(
                    self.server_received_ns - self.current_send_ns
                )
                self.current_sample.server_request_deserialization_ms = ns_to_ms(
                    request_decode_end - request_decode_start
                )
                self.current_sample.server_response_serialization_ms = ns_to_ms(
                    response_encode_end - response_encode_start
                )
                self.current_sample.response_size_bytes = len(response_bytes)
                self.server_reply_sent_ns = now_ns()
                await self.nc.publish(msg.reply, response_bytes)

            self.subscription = await self.nc.subscribe(self.args.subject, cb=handler)
        else:
            async def handler(msg) -> None:
                self.server_received_ns = now_ns()
                request_decode_start = now_ns()
                decoded = PlainJsonCodec.decode(msg.data)
                request_decode_end = now_ns()
                response_encode_start = now_ns()
                response_bytes = PlainJsonCodec.encode(decoded)
                response_encode_end = now_ns()
                assert self.current_sample is not None
                self.current_sample.request_network_transit_ms = ns_to_ms(
                    self.server_received_ns - self.current_send_ns
                )
                self.current_sample.server_request_deserialization_ms = ns_to_ms(
                    request_decode_end - request_decode_start
                )
                self.current_sample.server_response_serialization_ms = ns_to_ms(
                    response_encode_end - response_encode_start
                )
                self.current_sample.response_size_bytes = len(response_bytes)
                self.server_reply_sent_ns = now_ns()
                await self.nc.publish(msg.reply, response_bytes)

            self.subscription = await self.nc.subscribe(self.args.subject, cb=handler)

        await self.nc.flush()

    async def _telepact_echo(self, _function_name: str, _message: Message) -> Message:
        return Message({}, {"Ok_": copy.deepcopy(self.server_response_payload)})

    def _telepact_on_request(self, _message: Message) -> None:
        self.server_on_request_ns = now_ns()

    def _telepact_on_response(self, _message: Message) -> None:
        self.server_on_response_ns = now_ns()

    def _start_telepact_client(self) -> None:
        assert self.nc is not None

        async def adapter(request_message: Message, serializer) -> Message:
            assert self.current_sample is not None
            serialize_start = now_ns()
            request_bytes = serializer.serialize(request_message)
            serialize_end = now_ns()
            self.current_sample.request_serialization_ms = ns_to_ms(serialize_end - serialize_start)
            self.current_sample.request_size_bytes = len(request_bytes)
            self.last_request_was_binary = request_bytes[0] == 0x92
            self.current_send_ns = now_ns()
            response_msg = await self.nc.request(self.args.subject, request_bytes, timeout=10)
            response_receive_ns = now_ns()
            self.current_sample.response_network_transit_ms = ns_to_ms(response_receive_ns - self.server_reply_sent_ns)
            deserialize_start = now_ns()
            response_message = serializer.deserialize(response_msg.data)
            deserialize_end = now_ns()
            self.current_sample.response_deserialization_ms = ns_to_ms(deserialize_end - deserialize_start)
            return response_message

        client_options = Client.Options()
        client_options.use_binary = self.args.method != "telepact-json"
        client_options.always_send_json = self.args.method == "telepact-json"
        self.telepact_client = Client(adapter, client_options)

    async def run(self) -> dict[str, Any]:
        warmup = self.args.warmup
        if self.args.method in {"telepact-binary", "telepact-packed-binary"}:
            warmup = max(warmup, 1)

        handshake_complete = self.args.method not in {"telepact-binary", "telepact-packed-binary"}
        for _ in range(warmup):
            sample, steady_state = await self._run_once(record=False)
            handshake_complete = handshake_complete or steady_state

        while not handshake_complete:
            _, handshake_complete = await self._run_once(record=False)

        samples = []
        for _ in range(self.args.iterations):
            sample, _ = await self._run_once(record=True)
            samples.append(sample.as_dict())

        return {
            "language": "python",
            "method": self.args.method,
            "collection_shape": self.args.collection_shape,
            "data_shape": self.args.data_shape,
            "network_latency": "close" if "127.0.0.1" in self.args.nats_url else "far",
            "warmup_iterations": warmup,
            "measured_iterations": self.args.iterations,
            "samples": samples,
        }

    async def _run_once(self, record: bool) -> tuple[Sample, bool]:
        if self.args.method.startswith("telepact"):
            sample, steady_state = await self._run_telepact_once()
        elif self.args.method == "protobuf":
            sample, steady_state = await self._run_protobuf_once()
        else:
            sample, steady_state = await self._run_plain_json_once()
        if not record:
            return sample, steady_state
        return sample, steady_state

    async def _run_telepact_once(self) -> tuple[Sample, bool]:
        assert self.telepact_client is not None
        sample = Sample()
        self.current_sample = sample
        headers: dict[str, Any] = {}
        if self.args.method == "telepact-packed-binary":
            headers["@pac_"] = True
        await self.telepact_client.request(Message(headers, {"fn.echo": copy.deepcopy(self.telepact_payload)}))
        steady_state = self.args.method == "telepact-json" or (
            self.last_request_was_binary and self.last_response_was_binary
        )
        return sample, steady_state

    async def _run_protobuf_once(self) -> tuple[Sample, bool]:
        assert self.nc is not None
        sample = Sample()
        self.current_sample = sample
        serialize_start = now_ns()
        request_bytes = self.protobuf.encode_request(self.payload)
        serialize_end = now_ns()
        sample.request_serialization_ms = ns_to_ms(serialize_end - serialize_start)
        sample.request_size_bytes = len(request_bytes)
        self.current_send_ns = now_ns()
        response_msg = await self.nc.request(self.args.subject, request_bytes, timeout=10)
        response_receive_ns = now_ns()
        sample.response_network_transit_ms = ns_to_ms(response_receive_ns - self.server_reply_sent_ns)
        deserialize_start = now_ns()
        self.protobuf.decode_response(response_msg.data)
        deserialize_end = now_ns()
        sample.response_deserialization_ms = ns_to_ms(deserialize_end - deserialize_start)
        return sample, True

    async def _run_plain_json_once(self) -> tuple[Sample, bool]:
        assert self.nc is not None
        sample = Sample()
        self.current_sample = sample
        serialize_start = now_ns()
        request_bytes = PlainJsonCodec.encode(self.payload)
        serialize_end = now_ns()
        sample.request_serialization_ms = ns_to_ms(serialize_end - serialize_start)
        sample.request_size_bytes = len(request_bytes)
        self.current_send_ns = now_ns()
        response_msg = await self.nc.request(self.args.subject, request_bytes, timeout=10)
        response_receive_ns = now_ns()
        sample.response_network_transit_ms = ns_to_ms(response_receive_ns - self.server_reply_sent_ns)
        deserialize_start = now_ns()
        PlainJsonCodec.decode(response_msg.data)
        deserialize_end = now_ns()
        sample.response_deserialization_ms = ns_to_ms(deserialize_end - deserialize_start)
        return sample, True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", required=True)
    parser.add_argument("--collection-shape", required=True)
    parser.add_argument("--data-shape", required=True)
    parser.add_argument("--nats-url", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--iterations", type=int, required=True)
    parser.add_argument("--warmup", type=int, required=True)
    parser.add_argument("--payloads", required=True)
    parser.add_argument("--schema-dir", required=True)
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    async with BenchmarkRunner(args) as runner:
        print(json.dumps(await runner.run()))


if __name__ == "__main__":
    asyncio.run(async_main())
