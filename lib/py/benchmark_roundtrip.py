from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
import statistics
import time
from typing import Any, cast

from telepact import Client, FunctionRouter, Message, Server, TelepactSchema


SCHEMA = [
    {
        "struct.DenseRow": {
            "accountId": "integer",
            "name": "string",
            "region": "string",
            "unitPrice": "number",
            "quantity": "integer",
            "rating": "number",
            "active": "boolean",
        }
    },
    {
        "struct.SparseDetail": {
            "kind": "string",
            "score!": "number",
            "note!": "string?",
        }
    },
    {
        "struct.SparseRow": {
            "accountId": "integer",
            "name": "string",
            "nickname!": "string?",
            "score!": "number?",
            "note!": "string?",
            "detail!": "struct.SparseDetail?",
        }
    },
    {
        "struct.NestedLeaf": {
            "label": "string",
            "amount": "number",
        }
    },
    {
        "struct.NestedMeta": {
            "source": "string",
            "level": "integer",
            "leaf": "struct.NestedLeaf",
        }
    },
    {
        "struct.NestedRow": {
            "accountId": "integer",
            "name": "string",
            "primary": "struct.NestedMeta",
            "secondary!": "struct.NestedMeta?",
        }
    },
    {
        "fn.benchDenseRows": {
            "items": ["struct.DenseRow"]
        },
        "->": [
            {
                "Ok_": {
                    "items": ["struct.DenseRow"]
                }
            }
        ]
    },
    {
        "fn.benchSparseRows": {
            "items": ["struct.SparseRow"]
        },
        "->": [
            {
                "Ok_": {
                    "items": ["struct.SparseRow"]
                }
            }
        ]
    },
    {
        "fn.benchNestedRows": {
            "items": ["struct.NestedRow"]
        },
        "->": [
            {
                "Ok_": {
                    "items": ["struct.NestedRow"]
                }
            }
        ]
    },
]


@dataclass(frozen=True)
class Scenario:
    name: str
    function_name: str
    size: int


SCENARIOS = (
    Scenario("tiny-dense", "fn.benchDenseRows", 1),
    Scenario("medium-dense", "fn.benchDenseRows", 48),
    Scenario("medium-sparse", "fn.benchSparseRows", 32),
    Scenario("medium-nested", "fn.benchNestedRows", 20),
)

METHODS = (
    "telepact-json",
    "telepact-binary",
    "telepact-packed-binary",
)

METRICS = (
    "clientRequestSerializationTimeNs",
    "serverRequestDeserializationTimeNs",
    "serverResponseSerializationTimeNs",
    "clientResponseDeserializationTimeNs",
    "serializedRequestSizeBytes",
    "serializedResponseSizeBytes",
    "roundTripTimeNs",
)


def build_dense_rows(size: int) -> list[dict[str, object]]:
    regions = ("na", "eu", "apac", "latam")
    return [
        {
            "accountId": 100_000 + index,
            "name": f"customer-{index:04d}",
            "region": regions[index % len(regions)],
            "unitPrice": 19.5 + index * 0.125,
            "quantity": 1 + (index % 11),
            "rating": 0.5 + (index % 5) * 0.75,
            "active": index % 2 == 0,
        }
        for index in range(size)
    ]


def build_sparse_rows(size: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(size):
        row: dict[str, object] = {
            "accountId": 200_000 + index,
            "name": f"sparse-{index:04d}",
        }
        if index % 2 == 0:
            row["nickname!"] = f"nick-{index:04d}"
        elif index % 3 == 0:
            row["nickname!"] = None

        if index % 3 == 0:
            row["score!"] = 70.0 + index / 10.0
        elif index % 3 == 1:
            row["score!"] = None

        if index % 4 == 0:
            row["note!"] = f"note-{index:04d}"
        elif index % 4 == 1:
            row["note!"] = None

        if index % 5 == 0:
            row["detail!"] = {
                "kind": "full",
                "score!": 10.0 + index,
                "note!": f"detail-{index:04d}",
            }
        elif index % 5 == 1:
            row["detail!"] = None

        rows.append(row)
    return rows


def build_nested_rows(size: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(size):
        primary = {
            "source": "primary",
            "level": index % 7,
            "leaf": {
                "label": f"leaf-primary-{index:04d}",
                "amount": 100.0 + index * 1.5,
            },
        }
        row: dict[str, object] = {
            "accountId": 300_000 + index,
            "name": f"nested-{index:04d}",
            "primary": primary,
        }
        if index % 2 == 0:
            row["secondary!"] = {
                "source": "secondary",
                "level": (index + 1) % 7,
                "leaf": {
                    "label": f"leaf-secondary-{index:04d}",
                    "amount": 200.0 + index * 2.25,
                },
            }
        elif index % 3 == 0:
            row["secondary!"] = None
        rows.append(row)
    return rows


def build_payload(function_name: str, size: int) -> list[dict[str, object]]:
    if function_name == "fn.benchDenseRows":
        return build_dense_rows(size)
    if function_name == "fn.benchSparseRows":
        return build_sparse_rows(size)
    if function_name == "fn.benchNestedRows":
        return build_nested_rows(size)
    raise ValueError(function_name)


def percentile(values: list[float], fraction: float) -> float:
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    ratio = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * ratio


def summarize_metric(values: list[float]) -> dict[str, float]:
    return {
        "min": min(values),
        "max": max(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "p95": percentile(values, 0.95),
    }


def build_request(function_name: str, payload: list[dict[str, object]], method: str) -> Message:
    headers: dict[str, object] = {}
    if method == "telepact-packed-binary":
        headers["@pac_"] = True
    return Message(headers, {function_name: {"items": payload}})


def build_schema() -> TelepactSchema:
    return TelepactSchema.from_json(json.dumps(SCHEMA))


def build_router() -> FunctionRouter:
    async def echo_route(function_name: str, request_message: Message) -> Message:
        payload = cast(dict[str, object], request_message.body[function_name])
        return Message({}, {"Ok_": {"items": payload["items"]}})

    return FunctionRouter(
        {
            "fn.benchDenseRows": echo_route,
            "fn.benchSparseRows": echo_route,
            "fn.benchNestedRows": echo_route,
        }
    )


def build_server(schema: TelepactSchema, server_state: dict[str, Any]) -> Server:
    options = Server.Options()
    options.auth_required = False
    options.on_request = lambda _message: server_state.__setitem__("afterDeserializeNs", time.perf_counter_ns())
    options.on_response = lambda _message: server_state.__setitem__("beforeSerializeNs", time.perf_counter_ns())
    return Server(schema, build_router(), options)


def build_client(server: Server, method: str) -> Client:
    async def adapter(message: Message, serializer: Any) -> Message:
        request_bytes = serializer.serialize(message)
        response = await server.process(request_bytes)
        return serializer.deserialize(response.bytes)

    options = Client.Options()
    options.use_binary = method != "telepact-json"
    options.always_send_json = method == "telepact-json"
    return Client(adapter, options)


async def run_roundtrip_sample(server: Server, client: Client, server_state: dict[str, Any], request_message: Message) -> dict[str, int]:
    request_start = time.perf_counter_ns()
    server_state.clear()
    response_message = await client.request(request_message)
    response_end = time.perf_counter_ns()
    assert response_message.body["Ok_"] == request_message.get_body_payload()

    request_metrics = cast(dict[str, int], cast(dict[str, object], server_state)["requestMetrics"])
    response_metrics = cast(dict[str, int], cast(dict[str, object], server_state)["responseMetrics"])

    return {
        "clientRequestSerializationTimeNs": request_metrics["serializeNs"],
        "serverRequestDeserializationTimeNs": server_state["afterDeserializeNs"] - request_metrics["sentAtNs"],
        "serverResponseSerializationTimeNs": response_metrics["responseSentAtNs"] - server_state["beforeSerializeNs"],
        "clientResponseDeserializationTimeNs": response_metrics["deserializeNs"],
        "serializedRequestSizeBytes": request_metrics["requestBytes"],
        "serializedResponseSizeBytes": response_metrics["responseBytes"],
        "roundTripTimeNs": response_end - request_start,
    }


def patch_client_adapter(server: Server, client: Client, server_state: dict[str, Any]) -> None:
    async def adapter(message: Message, serializer: Any) -> Message:
        serialize_start = time.perf_counter_ns()
        request_bytes = serializer.serialize(message)
        serialize_end = time.perf_counter_ns()
        cast(dict[str, object], server_state)["requestMetrics"] = {
            "serializeNs": serialize_end - serialize_start,
            "requestBytes": len(request_bytes),
            "sentAtNs": time.perf_counter_ns(),
        }
        response = await server.process(request_bytes)
        deserialize_start = time.perf_counter_ns()
        response_message = serializer.deserialize(response.bytes)
        deserialize_end = time.perf_counter_ns()
        cast(dict[str, object], server_state)["responseMetrics"] = {
            "deserializeNs": deserialize_end - deserialize_start,
            "responseBytes": len(response.bytes),
            "responseSentAtNs": time.perf_counter_ns(),
        }
        return response_message

    client.adapter = adapter


def run_codec_sample(client: Client, server: Server, request_message: Message) -> dict[str, int]:
    client_serializer = client.serializer
    server_serializer = server.serializer

    serialize_start = time.perf_counter_ns()
    request_bytes = client_serializer.serialize(request_message)
    serialize_end = time.perf_counter_ns()

    server_deserialize_start = time.perf_counter_ns()
    decoded_request = server_serializer.deserialize(request_bytes)
    server_deserialize_end = time.perf_counter_ns()

    response_message = Message({}, {"Ok_": {"items": decoded_request.get_body_payload()["items"]}})

    server_serialize_start = time.perf_counter_ns()
    response_bytes = server_serializer.serialize(response_message)
    server_serialize_end = time.perf_counter_ns()

    client_deserialize_start = time.perf_counter_ns()
    decoded_response = client_serializer.deserialize(response_bytes)
    client_deserialize_end = time.perf_counter_ns()

    assert decoded_response.body["Ok_"] == request_message.get_body_payload()

    return {
        "clientRequestSerializationTimeNs": serialize_end - serialize_start,
        "serverRequestDeserializationTimeNs": server_deserialize_end - server_deserialize_start,
        "serverResponseSerializationTimeNs": server_serialize_end - server_serialize_start,
        "clientResponseDeserializationTimeNs": client_deserialize_end - client_deserialize_start,
        "serializedRequestSizeBytes": len(request_bytes),
        "serializedResponseSizeBytes": len(response_bytes),
        "roundTripTimeNs": client_deserialize_end - serialize_start,
    }


async def run_scenario(iterations: int, warmup_iterations: int, scenario: Scenario, method: str, mode: str) -> dict[str, object]:
    schema = build_schema()
    server_state: dict[str, Any] = {}
    server = build_server(schema, server_state)
    client = build_client(server, method)
    patch_client_adapter(server, client, server_state)
    payload = build_payload(scenario.function_name, scenario.size)
    request_message = build_request(scenario.function_name, payload, method)

    for _ in range(warmup_iterations):
        if mode == "codec":
            run_codec_sample(client, server, request_message)
        else:
            await run_roundtrip_sample(server, client, server_state, request_message)

    samples: list[dict[str, int]] = []
    for _ in range(iterations):
        if mode == "codec":
            samples.append(run_codec_sample(client, server, request_message))
        else:
            samples.append(await run_roundtrip_sample(server, client, server_state, request_message))

    return {
        "scenario": scenario.name,
        "function": scenario.function_name,
        "size": scenario.size,
        "method": method,
        "mode": mode,
        "iterations": iterations,
        "warmupIterations": warmup_iterations,
        "metrics": {
            metric: summarize_metric([float(sample[metric]) for sample in samples])
            for metric in METRICS
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--warmup-iterations", type=int, default=3)
    parser.add_argument("--mode", choices=("roundtrip", "codec", "both"), default="both")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


async def main_async() -> list[dict[str, object]]:
    args = parse_args()
    modes = ("roundtrip", "codec") if args.mode == "both" else (args.mode,)
    results: list[dict[str, object]] = []

    for mode in modes:
        for scenario in SCENARIOS:
            for method in METHODS:
                results.append(
                    await run_scenario(
                        iterations=args.iterations,
                        warmup_iterations=args.warmup_iterations,
                        scenario=scenario,
                        method=method,
                        mode=mode,
                    )
                )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2) + "\n")
    else:
        print(json.dumps(results, indent=2))
    return results


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()