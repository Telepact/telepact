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
import statistics
import time
from pathlib import Path
from typing import Any

from telepact import Client, FunctionRouter, Message, Server, TelepactSchema

from .common import PERFORMANCE_ROOT, utc_now_iso, write_json

COLLECTION_SHAPES = (
    "single",
    "small-list",
    "big-list",
    "really-big-list",
    "huge-list",
)
METHODS = (
    "telepact-binary",
    "telepact-packed-binary",
)
PAYLOADS_PATH = PERFORMANCE_ROOT / "payloads" / "cases.json"
DEFAULT_OUTPUT = PERFORMANCE_ROOT / "results" / "fixed-schema-python-benchmark.json"
FIXED_SCHEMA_JSON = json.dumps([
    {
        "struct.Item": {
            "accountId": "integer",
            "customerName": "string",
            "region": "string",
            "unitPrice": "number",
            "quantity": "integer",
        }
    },
    {
        "fn.roundTrip": {
            "items": ["struct.Item"],
        },
        "->": [
            {
                "Ok_": {
                    "items": ["struct.Item"],
                }
            }
        ],
    },
])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=150)
    parser.add_argument("--warmup-iterations", type=int, default=30)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def load_typical_payloads() -> dict[str, list[dict[str, object]]]:
    payloads = json.loads(PAYLOADS_PATH.read_text())
    return payloads["typical"]


async def echo_route(function_name_unused: str, request_message: Message) -> Message:
    return Message({}, {"Ok_": {"items": request_message.body[function_name_unused]["items"]}})


async def run_scenario(schema: TelepactSchema,
                       payload: list[dict[str, object]],
                       collection_shape: str,
                       method: str,
                       iterations: int,
                       warmup_iterations: int) -> dict[str, object]:
    router = FunctionRouter({"fn.roundTrip": echo_route})
    options = Server.Options()
    options.auth_required = False
    server = Server(schema, router, options)

    async def adapter(message: Message, serializer: Any) -> Message:
        request_bytes = serializer.serialize(message)
        adapter.last_request_size = len(request_bytes)
        response = await server.process(request_bytes)
        adapter.last_response_size = len(response.bytes)
        return serializer.deserialize(response.bytes)

    adapter.last_request_size = 0
    adapter.last_response_size = 0

    client_options = Client.Options()
    client_options.use_binary = True
    client_options.always_send_json = False
    client = Client(adapter, client_options)
    request_headers = {"@pac_": True} if method == "telepact-packed-binary" else {}

    async def request_once() -> int:
        started = time.perf_counter_ns()
        response = await client.request(Message(request_headers, {"fn.roundTrip": {"items": payload}}))
        finished = time.perf_counter_ns()
        assert response.body == {"Ok_": {"items": payload}}
        return finished - started

    for _ in range(warmup_iterations):
        await request_once()

    samples = [await request_once() for _ in range(iterations)]
    ordered = sorted(samples)
    return {
        "collectionShape": collection_shape,
        "method": method,
        "medianTotalLatencyNs": statistics.median(samples),
        "meanTotalLatencyNs": statistics.fmean(samples),
        "p95TotalLatencyNs": ordered[int((len(ordered) - 1) * 0.95)],
        "requestSizeBytes": adapter.last_request_size,
        "responseSizeBytes": adapter.last_response_size,
    }


async def async_main(args: argparse.Namespace) -> None:
    schema = TelepactSchema.from_json(FIXED_SCHEMA_JSON)
    payloads = load_typical_payloads()
    results: list[dict[str, object]] = []

    for collection_shape in COLLECTION_SHAPES:
        payload = payloads[collection_shape]
        for method in METHODS:
            results.append(await run_scenario(
                schema,
                payload,
                collection_shape,
                method,
                args.iterations,
                args.warmup_iterations,
            ))

    write_json(args.output, {
        "metadata": {
            "generatedAt": utc_now_iso(),
            "iterations": args.iterations,
            "warmupIterations": args.warmup_iterations,
            "collectionShapes": list(COLLECTION_SHAPES),
            "methods": list(METHODS),
            "schema": "fixed-inline-typical-item",
        },
        "results": results,
    })
    print(args.output)


def main() -> None:
    asyncio.run(async_main(parse_args()))


if __name__ == "__main__":
    main()