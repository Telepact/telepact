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
import json
from pathlib import Path
import time
from typing import Any

from telepact import Client, FunctionRouter, Message, Server, TelepactSchema

from . import benchmark_pb2
from .common import (
    COLLECTION_SHAPES,
    DATA_SHAPES,
    FUNCTION_NAMES,
    METHODS,
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


def parse_csv(value: str, allowed: tuple[str, ...]) -> list[str]:
    selected = [item for item in value.split(",") if item]
    if not selected:
        return list(allowed)
    unknown = sorted(set(selected) - set(allowed))
    if unknown:
        raise ValueError(f"unknown values: {', '.join(unknown)}")
    return selected


class PythonWorker:
    def __init__(self, iterations: int, warmup_iterations: int, data_shapes: list[str], collection_shapes: list[str], methods: list[str]):
        self.iterations = iterations
        self.warmup_iterations = warmup_iterations
        self.data_shapes = data_shapes
        self.collection_shapes = collection_shapes
        self.methods = methods
        self.payloads = load_payloads()
        self.schema = TelepactSchema.from_directory(str(SCHEMA_DIR))

    def run(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for scenario in iter_scenarios(self.data_shapes, self.collection_shapes, self.methods):
            payload = self.payloads[scenario.data_shape][scenario.collection_shape]
            warmup_iterations = self._warmup_iterations_for(scenario)
            benchmark_once = self._create_benchmark(scenario)
            for _ in range(warmup_iterations):
                benchmark_once(payload)
            samples = [benchmark_once(payload) for _ in range(self.iterations)]
            results.append(scenario_record("python", scenario, self.iterations, warmup_iterations, samples))
        return results

    def _warmup_iterations_for(self, scenario: Scenario) -> int:
        if scenario.method in {"telepact-binary", "telepact-packed-binary"}:
            return self.warmup_iterations
        return 0

    def _create_benchmark(self, scenario: Scenario):
        if scenario.method.startswith("telepact"):
            return self._create_telepact_benchmark(scenario)
        if scenario.method == "protobuf":
            return self._create_protobuf_benchmark(scenario)
        return self._create_plain_json_benchmark(scenario)

    def _create_plain_json_benchmark(self, scenario: Scenario):
        function_name = PLAIN_FUNCTION_NAMES[scenario.data_shape]

        def benchmark_once(payload: list[dict[str, Any]]) -> dict[str, Any]:
            request_object = {"function": function_name, "items": payload}
            serialize_start = time.perf_counter_ns()
            request_bytes = json.dumps(request_object, separators=(",", ":")).encode()
            request_serialize_end = time.perf_counter_ns()
            request_deserialize_start = time.perf_counter_ns()
            request_round_trip = json.loads(request_bytes)
            request_deserialize_end = time.perf_counter_ns()
            assert request_round_trip["items"] == payload

            response_object = {"function": request_round_trip["function"], "items": request_round_trip["items"]}
            response_serialize_start = time.perf_counter_ns()
            response_bytes = json.dumps(response_object, separators=(",", ":")).encode()
            response_serialize_end = time.perf_counter_ns()
            response_deserialize_start = time.perf_counter_ns()
            response_round_trip = json.loads(response_bytes)
            response_deserialize_end = time.perf_counter_ns()
            assert response_round_trip["items"] == payload

            return {
                "requestSerializationTimeNs": request_serialize_end - serialize_start,
                "requestDeserializationTimeNs": request_deserialize_end - request_deserialize_start,
                "responseSerializationTimeNs": response_serialize_end - response_serialize_start,
                "responseDeserializationTimeNs": response_deserialize_end - response_deserialize_start,
                "serializedRequestSizeBytes": len(request_bytes),
                "serializedResponseSizeBytes": len(response_bytes),
            }

        return benchmark_once

    def _create_protobuf_benchmark(self, scenario: Scenario):
        request_type_name, response_type_name, field_name = PROTODESC[scenario.data_shape]
        request_type = getattr(benchmark_pb2, request_type_name)
        response_type = getattr(benchmark_pb2, response_type_name)
        item_descriptor = request_type.DESCRIPTOR.fields_by_name[field_name].message_type
        item_type = getattr(benchmark_pb2, item_descriptor.name)

        def build_request(payload: list[dict[str, Any]]):
            message = request_type()
            getattr(message, field_name).extend(item_type(**item) for item in payload)
            return message

        def build_response(request_message) -> Any:
            response = response_type()
            getattr(response, field_name).extend(getattr(request_message, field_name))
            return response

        def benchmark_once(payload: list[dict[str, Any]]) -> dict[str, Any]:
            request_message = build_request(payload)
            request_serialize_start = time.perf_counter_ns()
            request_bytes = request_message.SerializeToString()
            request_serialize_end = time.perf_counter_ns()
            request_deserialize_start = time.perf_counter_ns()
            request_round_trip = request_type()
            request_round_trip.ParseFromString(request_bytes)
            request_deserialize_end = time.perf_counter_ns()
            assert len(getattr(request_round_trip, field_name)) == len(payload)

            response_message = build_response(request_round_trip)
            response_serialize_start = time.perf_counter_ns()
            response_bytes = response_message.SerializeToString()
            response_serialize_end = time.perf_counter_ns()
            response_deserialize_start = time.perf_counter_ns()
            response_round_trip = response_type()
            response_round_trip.ParseFromString(response_bytes)
            response_deserialize_end = time.perf_counter_ns()
            assert len(getattr(response_round_trip, field_name)) == len(payload)

            return {
                "requestSerializationTimeNs": request_serialize_end - request_serialize_start,
                "requestDeserializationTimeNs": request_deserialize_end - request_deserialize_start,
                "responseSerializationTimeNs": response_serialize_end - response_serialize_start,
                "responseDeserializationTimeNs": response_deserialize_end - response_deserialize_start,
                "serializedRequestSizeBytes": len(request_bytes),
                "serializedResponseSizeBytes": len(response_bytes),
            }

        return benchmark_once

    def _create_telepact_benchmark(self, scenario: Scenario):
        async def unused_adapter(_message: Message, _serializer) -> Message:
            raise RuntimeError("unused benchmark adapter")

        client = Client(unused_adapter, Client.Options())
        server_options = Server.Options()
        server_options.auth_required = False
        server = Server(self.schema, FunctionRouter({}), server_options)
        client_serializer = client.serializer
        server_serializer = server.serializer
        function_name = FUNCTION_NAMES[scenario.data_shape]

        def build_request_message(payload: list[dict[str, Any]]) -> Message:
            headers: dict[str, object] = {}
            if scenario.method != "telepact-json":
                headers["@binary_"] = True
            if scenario.method == "telepact-packed-binary":
                headers["@pac_"] = True
            return Message(headers, {function_name: {"items": payload}})

        def build_response_message(request_message: Message) -> Message:
            headers: dict[str, object] = {}
            if "@bin_" in request_message.headers:
                headers["@binary_"] = True
                headers["@clientKnownBinaryChecksums_"] = request_message.headers["@bin_"]
            if "@pac_" in request_message.headers:
                headers["@pac_"] = request_message.headers["@pac_"]
            return Message(headers, {"Ok_": {"items": request_message.body[function_name]["items"]}})

        def benchmark_once(payload: list[dict[str, Any]]) -> dict[str, Any]:
            request_message = build_request_message(payload)
            request_serialize_start = time.perf_counter_ns()
            request_bytes = client_serializer.serialize(request_message)
            request_serialize_end = time.perf_counter_ns()
            request_deserialize_start = time.perf_counter_ns()
            request_round_trip = server_serializer.deserialize(request_bytes)
            request_deserialize_end = time.perf_counter_ns()
            assert request_round_trip.body[function_name]["items"] == payload

            response_message = build_response_message(request_round_trip)
            response_serialize_start = time.perf_counter_ns()
            response_bytes = server_serializer.serialize(response_message)
            response_serialize_end = time.perf_counter_ns()
            response_deserialize_start = time.perf_counter_ns()
            response_round_trip = client_serializer.deserialize(response_bytes)
            response_deserialize_end = time.perf_counter_ns()
            assert response_round_trip.body["Ok_"]["items"] == payload

            return {
                "requestSerializationTimeNs": request_serialize_end - request_serialize_start,
                "requestDeserializationTimeNs": request_deserialize_end - request_deserialize_start,
                "responseSerializationTimeNs": response_serialize_end - response_serialize_start,
                "responseDeserializationTimeNs": response_deserialize_end - response_deserialize_start,
                "serializedRequestSizeBytes": len(request_bytes),
                "serializedResponseSizeBytes": len(response_bytes),
            }

        return benchmark_once


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, required=True)
    parser.add_argument("--warmup-iterations", type=int, required=True)
    parser.add_argument("--data-shapes", required=True)
    parser.add_argument("--collection-shapes", required=True)
    parser.add_argument("--methods", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_shapes = parse_csv(args.data_shapes, DATA_SHAPES)
    collection_shapes = parse_csv(args.collection_shapes, COLLECTION_SHAPES)
    methods = parse_csv(args.methods, METHODS)
    worker = PythonWorker(args.iterations, args.warmup_iterations, data_shapes, collection_shapes, methods)
    results = worker.run()
    write_json(Path(args.output), {
        "metadata": {
            "language": "python",
            "generatedAt": utc_now_iso(),
            "iterations": args.iterations,
            "warmupIterations": args.warmup_iterations,
            "dataShapes": data_shapes,
            "collectionShapes": collection_shapes,
            "methods": methods,
        },
        "scenarios": results,
    })


if __name__ == "__main__":
    main()
