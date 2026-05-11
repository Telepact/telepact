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
import copy
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Coroutine

import benchmark_pb2
import nats
from google.protobuf import json_format
from nats.aio.client import Client as NatsClient
from nats.aio.msg import Msg
from telepact import Client, FunctionRouter, Message, Server, TelepactSchema

ROOT = Path("/home/runner/work/telepact/telepact/test/performance")
CONFIG = json.loads((ROOT / "config" / "benchmark-config.json").read_text())
PAYLOADS = json.loads((ROOT / "config" / "payloads.json").read_text())
SCHEMA_DIR = str(ROOT / "schema")
TELEPACT_SCHEMA_PATH = ROOT / "schema" / "benchmark.telepact.json"
LANGUAGE = "python"
NATS_URL = os.environ.get("NATS_URL", CONFIG["natsUrl"])
SERVER_HEADER_NAMES = {
    "received_wall_ns": "x-telepact-perf-server-received-wall-ns",
    "request_deserialize_ns": "x-telepact-perf-server-request-deserialize-ns",
    "response_serialize_ns": "x-telepact-perf-server-response-serialize-ns",
    "sent_wall_ns": "x-telepact-perf-server-sent-wall-ns",
}


def subject_for(method: str, data_shape: str) -> str:
    suffix = CONFIG["dataShapes"][data_shape]["subjectSuffix"]
    return f"{CONFIG['subjectPrefix']}.{LANGUAGE}.{method}.{suffix}"



def metric_headers(measurement: dict[str, int]) -> dict[str, str]:
    return {
        SERVER_HEADER_NAMES["received_wall_ns"]: str(measurement["received_wall_ns"]),
        SERVER_HEADER_NAMES["request_deserialize_ns"]: str(measurement["request_deserialize_ns"]),
        SERVER_HEADER_NAMES["response_serialize_ns"]: str(measurement["response_serialize_ns"]),
        SERVER_HEADER_NAMES["sent_wall_ns"]: str(measurement["sent_wall_ns"]),
    }



def parse_metric_headers(headers: Any) -> dict[str, int]:
    if headers is None:
        raise RuntimeError("Missing NATS headers on benchmark response")
    return {
        "received_wall_ns": int(headers.get(SERVER_HEADER_NAMES["received_wall_ns"])),
        "request_deserialize_ns": int(headers.get(SERVER_HEADER_NAMES["request_deserialize_ns"])),
        "response_serialize_ns": int(headers.get(SERVER_HEADER_NAMES["response_serialize_ns"])),
        "sent_wall_ns": int(headers.get(SERVER_HEADER_NAMES["sent_wall_ns"])),
    }



def round_trip_sample(
    request_serialize_ns: int,
    request_size_bytes: int,
    request_sent_wall_ns: int,
    server_metrics: dict[str, int],
    response_size_bytes: int,
    response_received_wall_ns: int,
    response_deserialize_ns: int,
    round_trip_ns: int,
) -> dict[str, int]:
    return {
        "client_request_serialize_ns": request_serialize_ns,
        "request_size_bytes": request_size_bytes,
        "request_network_transit_ns": max(0, server_metrics["received_wall_ns"] - request_sent_wall_ns),
        "server_request_deserialize_ns": server_metrics["request_deserialize_ns"],
        "server_response_serialize_ns": server_metrics["response_serialize_ns"],
        "response_size_bytes": response_size_bytes,
        "response_network_transit_ns": max(0, response_received_wall_ns - server_metrics["sent_wall_ns"]),
        "client_response_deserialize_ns": response_deserialize_ns,
        "round_trip_ns": round_trip_ns,
    }



def telepact_message(function_name: str, payload: dict[str, Any], packed: bool) -> Message:
    headers: dict[str, object] = {}
    if packed:
        headers["@pac_"] = True
    return Message(headers, {function_name: copy.deepcopy(payload)})



def protobuf_request_factory(data_shape: str, payload: dict[str, Any]) -> tuple[Any, Callable[[bytes], Any], Callable[[Any], Any]]:
    if data_shape == "typical_data":
        request = json_format.ParseDict(payload, benchmark_pb2.TypicalRequest())
        return request, benchmark_pb2.TypicalResponse.FromString, lambda req: benchmark_pb2.TypicalResponse(items=req.items)
    if data_shape == "all_strings":
        request = json_format.ParseDict(payload, benchmark_pb2.AllStringsRequest())
        return request, benchmark_pb2.AllStringsResponse.FromString, lambda req: benchmark_pb2.AllStringsResponse(items=req.items)
    if data_shape == "all_numbers":
        request = json_format.ParseDict(payload, benchmark_pb2.AllNumbersRequest())
        return request, benchmark_pb2.AllNumbersResponse.FromString, lambda req: benchmark_pb2.AllNumbersResponse(items=req.items)
    raise ValueError(data_shape)


def protobuf_message_to_payload(data_shape: str, message: Any) -> dict[str, Any]:
    if data_shape == "typical_data":
        return {
            "items": [
                {
                    "primaryText": item.primary_text,
                    "secondaryText": item.secondary_text,
                    "primaryInt": int(item.primary_int),
                    "secondaryInt": int(item.secondary_int),
                    "primaryNumber": float(item.primary_number),
                    "secondaryNumber": float(item.secondary_number),
                }
                for item in message.items
            ]
        }
    if data_shape == "all_strings":
        return {
            "items": [
                {
                    "alpha": item.alpha,
                    "beta": item.beta,
                    "gamma": item.gamma,
                    "delta": item.delta,
                    "epsilon": item.epsilon,
                    "zeta": item.zeta,
                }
                for item in message.items
            ]
        }
    if data_shape == "all_numbers":
        return {
            "items": [
                {
                    "firstInt": int(item.first_int),
                    "secondInt": int(item.second_int),
                    "thirdInt": int(item.third_int),
                    "firstNumber": float(item.first_number),
                    "secondNumber": float(item.second_number),
                    "thirdNumber": float(item.third_number),
                }
                for item in message.items
            ]
        }
    raise ValueError(data_shape)


async def publish_reply(connection: NatsClient, msg: Msg, payload: bytes, headers: dict[str, str]) -> None:
    await connection.publish(msg.reply, payload, headers=headers)


async def start_servers(connection: NatsClient) -> list[Any]:
    subscriptions = []
    telepact_schema = TelepactSchema.from_file_json_map(
        {TELEPACT_SCHEMA_PATH.name: TELEPACT_SCHEMA_PATH.read_text()}
    )

    async def echo_route(_function_name: str, request_message: Message) -> Message:
        return Message({}, {"Ok_": copy.deepcopy(request_message.get_body_payload())})

    telepact_current: dict[str, int] | None = None
    telepact_options = Server.Options()
    telepact_options.auth_required = False

    def on_request(_message: Message) -> None:
        if telepact_current is not None:
            telepact_current["request_deserialize_ns"] = time.perf_counter_ns() - telepact_current["start_perf_ns"]

    def on_response(_message: Message) -> None:
        if telepact_current is not None:
            telepact_current["serialize_start_ns"] = time.perf_counter_ns()

    telepact_options.on_request = on_request
    telepact_options.on_response = on_response
    telepact_server = Server(
        telepact_schema,
        FunctionRouter(
            {
                "fn.echoTypical": echo_route,
                "fn.echoAllStrings": echo_route,
                "fn.echoAllNumbers": echo_route,
            }
        ),
        telepact_options,
    )

    async def telepact_handler(msg: Msg) -> None:
        nonlocal telepact_current
        measurement = {
            "start_perf_ns": time.perf_counter_ns(),
            "received_wall_ns": time.time_ns(),
            "request_deserialize_ns": 0,
            "serialize_start_ns": 0,
        }
        telepact_current = measurement
        response = await telepact_server.process(msg.data)
        serialize_start_ns = measurement["serialize_start_ns"] or time.perf_counter_ns()
        measurement["response_serialize_ns"] = time.perf_counter_ns() - serialize_start_ns
        measurement["sent_wall_ns"] = time.time_ns()
        telepact_current = None
        await publish_reply(connection, msg, response.bytes, metric_headers(measurement))

    async def plain_json_handler(data_shape: str, msg: Msg) -> None:
        measurement = {"received_wall_ns": time.time_ns()}
        deserialize_start_ns = time.perf_counter_ns()
        request_payload = json.loads(msg.data)
        measurement["request_deserialize_ns"] = time.perf_counter_ns() - deserialize_start_ns
        serialize_start_ns = time.perf_counter_ns()
        response_bytes = json.dumps(request_payload, separators=(",", ":")).encode("utf-8")
        measurement["response_serialize_ns"] = time.perf_counter_ns() - serialize_start_ns
        measurement["sent_wall_ns"] = time.time_ns()
        await publish_reply(connection, msg, response_bytes, metric_headers(measurement))

    async def protobuf_handler(data_shape: str, msg: Msg) -> None:
        measurement = {"received_wall_ns": time.time_ns()}
        request_message, response_from_bytes, response_builder = protobuf_request_factory(data_shape, PAYLOADS[data_shape]["single"])
        deserialize_start_ns = time.perf_counter_ns()
        parsed_request = request_message.__class__.FromString(msg.data)
        measurement["request_deserialize_ns"] = time.perf_counter_ns() - deserialize_start_ns
        serialize_start_ns = time.perf_counter_ns()
        response_bytes = response_builder(parsed_request).SerializeToString()
        measurement["response_serialize_ns"] = time.perf_counter_ns() - serialize_start_ns
        measurement["sent_wall_ns"] = time.time_ns()
        await publish_reply(connection, msg, response_bytes, metric_headers(measurement))

    for method in ("telepact_json", "telepact_binary", "telepact_packed_binary"):
        for data_shape in CONFIG["dataShapes"]:
            subscriptions.append(await connection.subscribe(subject_for(method, data_shape), cb=telepact_handler))

    for data_shape in CONFIG["dataShapes"]:
        async def plain_json_callback(msg: Msg, data_shape: str = data_shape) -> None:
            await plain_json_handler(data_shape, msg)

        async def protobuf_callback(msg: Msg, data_shape: str = data_shape) -> None:
            await protobuf_handler(data_shape, msg)

        subscriptions.append(
            await connection.subscribe(
                subject_for("plain_json", data_shape),
                cb=plain_json_callback,
            )
        )
        subscriptions.append(
            await connection.subscribe(
                subject_for("protobuf", data_shape),
                cb=protobuf_callback,
            )
        )

    await connection.flush()
    return subscriptions


async def run_telepact_case(connection: NatsClient, method: str, data_shape: str, collection_shape: str) -> dict[str, Any]:
    payload = PAYLOADS[data_shape][collection_shape]
    function_name = CONFIG["dataShapes"][data_shape]["telepactFunction"]
    samples: list[dict[str, int]] = []
    use_binary = method in {"telepact_binary", "telepact_packed_binary"}
    packed = method == "telepact_packed_binary"

    async def adapter(message: Message, serializer: Any) -> Message:
        request_start_ns = time.perf_counter_ns()
        request_bytes = serializer.serialize(message)
        request_serialize_ns = time.perf_counter_ns() - request_start_ns
        request_sent_wall_ns = time.time_ns()
        response_msg = await connection.request(
            subject_for(method, data_shape),
            request_bytes,
            timeout=CONFIG["requestTimeoutMs"] / 1000,
        )
        response_received_wall_ns = time.time_ns()
        server_metrics = parse_metric_headers(response_msg.headers)
        response_deserialize_start_ns = time.perf_counter_ns()
        response = serializer.deserialize(response_msg.data)
        response_deserialize_ns = time.perf_counter_ns() - response_deserialize_start_ns
        samples.append(
            round_trip_sample(
                request_serialize_ns,
                len(request_bytes),
                request_sent_wall_ns,
                server_metrics,
                len(response_msg.data),
                response_received_wall_ns,
                response_deserialize_ns,
                time.perf_counter_ns() - request_start_ns,
            )
        )
        return response

    options = Client.Options()
    options.use_binary = use_binary
    options.always_send_json = False if use_binary else True
    client = Client(adapter, options)

    handshake_iterations = CONFIG["binaryNegotiationWarmupIterations"] if use_binary else 0
    total_iterations = handshake_iterations + CONFIG["warmupIterations"] + CONFIG["steadyStateIterations"]

    for iteration in range(total_iterations):
        response = await client.request(telepact_message(function_name, payload, packed))
        if response.body != {"Ok_": payload}:
            raise RuntimeError(f"Unexpected Telepact response for {method}/{data_shape}/{collection_shape}")

    measured_samples = samples[handshake_iterations + CONFIG["warmupIterations"] :]
    return {
        "language": LANGUAGE,
        "method": method,
        "data_shape": data_shape,
        "collection_shape": collection_shape,
        "samples": measured_samples,
    }


async def run_plain_json_case(connection: NatsClient, data_shape: str, collection_shape: str) -> dict[str, Any]:
    payload = PAYLOADS[data_shape][collection_shape]
    samples: list[dict[str, int]] = []

    for iteration in range(CONFIG["warmupIterations"] + CONFIG["steadyStateIterations"]):
        request_start_ns = time.perf_counter_ns()
        request_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        request_serialize_ns = time.perf_counter_ns() - request_start_ns
        request_sent_wall_ns = time.time_ns()
        response_msg = await connection.request(
            subject_for("plain_json", data_shape),
            request_bytes,
            timeout=CONFIG["requestTimeoutMs"] / 1000,
        )
        response_received_wall_ns = time.time_ns()
        server_metrics = parse_metric_headers(response_msg.headers)
        response_deserialize_start_ns = time.perf_counter_ns()
        parsed_response = json.loads(response_msg.data)
        response_deserialize_ns = time.perf_counter_ns() - response_deserialize_start_ns
        if parsed_response != payload:
            raise RuntimeError(f"Unexpected JSON response for {data_shape}/{collection_shape}")
        samples.append(
            round_trip_sample(
                request_serialize_ns,
                len(request_bytes),
                request_sent_wall_ns,
                server_metrics,
                len(response_msg.data),
                response_received_wall_ns,
                response_deserialize_ns,
                time.perf_counter_ns() - request_start_ns,
            )
        )

    measured_samples = samples[CONFIG["warmupIterations"] :]
    return {
        "language": LANGUAGE,
        "method": "plain_json",
        "data_shape": data_shape,
        "collection_shape": collection_shape,
        "samples": measured_samples,
    }


async def run_protobuf_case(connection: NatsClient, data_shape: str, collection_shape: str) -> dict[str, Any]:
    payload = PAYLOADS[data_shape][collection_shape]
    request_message, response_from_bytes, _response_builder = protobuf_request_factory(data_shape, payload)
    response_as_dict = protobuf_message_to_payload(data_shape, response_from_bytes(request_message.SerializeToString()))
    if response_as_dict != payload:
        raise RuntimeError(f"Protobuf schema mismatch for {data_shape}/{collection_shape}")

    samples: list[dict[str, int]] = []
    for iteration in range(CONFIG["warmupIterations"] + CONFIG["steadyStateIterations"]):
        request_start_ns = time.perf_counter_ns()
        request_bytes = request_message.SerializeToString()
        request_serialize_ns = time.perf_counter_ns() - request_start_ns
        request_sent_wall_ns = time.time_ns()
        response_msg = await connection.request(
            subject_for("protobuf", data_shape),
            request_bytes,
            timeout=CONFIG["requestTimeoutMs"] / 1000,
        )
        response_received_wall_ns = time.time_ns()
        server_metrics = parse_metric_headers(response_msg.headers)
        response_deserialize_start_ns = time.perf_counter_ns()
        parsed_response = response_from_bytes(response_msg.data)
        response_deserialize_ns = time.perf_counter_ns() - response_deserialize_start_ns
        parsed_response_dict = protobuf_message_to_payload(data_shape, parsed_response)
        if parsed_response_dict != payload:
            raise RuntimeError(f"Unexpected protobuf response for {data_shape}/{collection_shape}")
        samples.append(
            round_trip_sample(
                request_serialize_ns,
                len(request_bytes),
                request_sent_wall_ns,
                server_metrics,
                len(response_msg.data),
                response_received_wall_ns,
                response_deserialize_ns,
                time.perf_counter_ns() - request_start_ns,
            )
        )

    measured_samples = samples[CONFIG["warmupIterations"] :]
    return {
        "language": LANGUAGE,
        "method": "protobuf",
        "data_shape": data_shape,
        "collection_shape": collection_shape,
        "samples": measured_samples,
    }


async def run_benchmark(output_path: Path) -> None:
    connection = await nats.connect(NATS_URL)
    await start_servers(connection)
    cases: list[dict[str, Any]] = []

    try:
        for data_shape in CONFIG["dataShapes"]:
            for collection_shape in CONFIG["collectionShapes"]:
                cases.append(await run_telepact_case(connection, "telepact_json", data_shape, collection_shape))
                cases.append(await run_telepact_case(connection, "telepact_binary", data_shape, collection_shape))
                cases.append(await run_telepact_case(connection, "telepact_packed_binary", data_shape, collection_shape))
                cases.append(await run_protobuf_case(connection, data_shape, collection_shape))
                cases.append(await run_plain_json_case(connection, data_shape, collection_shape))
    finally:
        await connection.drain()

    output_path.write_text(
        json.dumps(
            {
                "language": LANGUAGE,
                "nats_url": NATS_URL,
                "cases": cases,
            },
            indent=2,
        )
        + "\n"
    )


async def async_main(output_path: Path) -> None:
    await run_benchmark(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    asyncio.run(async_main(Path(args.output)))
