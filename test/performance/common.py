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

from dataclasses import dataclass
import json
import math
from pathlib import Path
import shutil
import statistics
from typing import Any, Iterable
import uuid

COLLECTION_SHAPES: dict[str, int] = {
    "single": 1,
    "small_list": 8,
    "big_list": 128,
    "really_big_list": 2048,
}

DATA_SHAPES = ("typical_data", "all_strings", "all_numbers")
METHODS = (
    "telepact_json",
    "telepact_binary",
    "telepact_packed_binary",
    "protobuf",
    "plain_json",
)
LANGUAGES = ("python", "typescript", "java")
LATENCIES = {
    "close": "nats://127.0.0.1:4222",
    "far": "nats://demo.nats.io:4222",
}
METRICS = (
    "client_request_serialize_ns",
    "request_size_bytes",
    "request_network_transit_ns",
    "server_request_deserialize_ns",
    "server_response_serialize_ns",
    "response_size_bytes",
    "response_network_transit_ns",
    "client_response_deserialize_ns",
)


@dataclass(frozen=True)
class Scenario:
    name: str
    function_name: str
    collection_shape: str
    data_shape: str
    request: dict[str, Any]
    response: dict[str, Any]


def _float_value(index: int, scale: float) -> float:
    return round(((index * scale) % 997) / 7.0 + (index % 5) * 0.125, 6)


def _typical_item(index: int) -> dict[str, Any]:
    return {
        "primaryId": f"item-{index:06d}",
        "secondaryId": f"group-{index % 97:03d}",
        "count": (index * 17) % 100_000,
        "ratio": _float_value(index, 13.0),
    }


def _string_item(index: int) -> dict[str, Any]:
    return {
        "alpha": f"alpha-{index:06d}",
        "beta": f"beta-{(index * 3) % 10_000:04d}",
        "gamma": f"gamma-{(index * 7) % 10_000:04d}",
        "delta": f"delta-{(index * 11) % 10_000:04d}",
    }


def _number_item(index: int) -> dict[str, Any]:
    return {
        "left": (index * 13) % 200_000,
        "right": (index * 29) % 300_000,
        "ratio": _float_value(index, 19.0),
        "offset": round(-250.0 + ((index * 23) % 10_000) / 9.0, 6),
    }


def _payload(data_shape: str, collection_shape: str) -> dict[str, Any]:
    count = COLLECTION_SHAPES[collection_shape]
    if data_shape == "typical_data":
        items = [_typical_item(i) for i in range(count)]
        return {"typicalSingle": items[0]} if collection_shape == "single" else {"typicalList": {"items": items}}
    if data_shape == "all_strings":
        items = [_string_item(i) for i in range(count)]
        return {"stringSingle": items[0]} if collection_shape == "single" else {"stringList": {"items": items}}
    items = [_number_item(i) for i in range(count)]
    return {"numberSingle": items[0]} if collection_shape == "single" else {"numberList": {"items": items}}


def build_scenarios() -> list[Scenario]:
    scenarios: list[Scenario] = []
    for collection_shape in COLLECTION_SHAPES:
        for data_shape in DATA_SHAPES:
            name = f"{collection_shape}__{data_shape}"
            payload = _payload(data_shape, collection_shape)
            function_name = {
                ("typical_data", "single"): "fn.typicalSingle",
                ("typical_data", "list"): "fn.typicalList",
                ("all_strings", "single"): "fn.stringSingle",
                ("all_strings", "list"): "fn.stringList",
                ("all_numbers", "single"): "fn.numberSingle",
                ("all_numbers", "list"): "fn.numberList",
            }[(data_shape, "single" if collection_shape == "single" else "list")]
            request = payload
            response = payload
            scenarios.append(
                Scenario(
                    name=name,
                    function_name=function_name,
                    collection_shape=collection_shape,
                    data_shape=data_shape,
                    request=request,
                    response=response,
                )
            )
    return scenarios


def write_manifest(path: Path, *, warmup_iterations: int, measure_iterations: int) -> None:
    scenarios = build_scenarios()
    payload = {
        "warmupIterations": warmup_iterations,
        "measureIterations": measure_iterations,
        "methods": list(METHODS),
        "collectionShapes": COLLECTION_SHAPES,
        "dataShapes": list(DATA_SHAPES),
        "scenarios": [
            {
                "name": scenario.name,
                "functionName": scenario.function_name,
                "collectionShape": scenario.collection_shape,
                "dataShape": scenario.data_shape,
                "request": scenario.request,
                "response": scenario.response,
            }
            for scenario in scenarios
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_values(values: list[float | int]) -> dict[str, float | int]:
    ordered = sorted(values)
    count = len(ordered)
    if count == 0:
        raise ValueError("cannot summarize empty sample set")
    mean = statistics.fmean(ordered)
    median = statistics.median(ordered)
    stdev = statistics.stdev(ordered) if count > 1 else 0.0
    margin = 1.96 * (stdev / math.sqrt(count)) if count > 1 else 0.0
    index_95 = min(count - 1, math.ceil(0.95 * count) - 1)
    return {
        "count": count,
        "min": ordered[0],
        "max": ordered[-1],
        "mean": mean,
        "median": median,
        "p95": ordered[index_95],
        "stdev": stdev,
        "mean_confidence_low": mean - margin,
        "mean_confidence_high": mean + margin,
    }


def summarize_samples(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for sample in samples:
        key = (
            sample["language"],
            sample["latency"],
            sample["method"],
            sample["scenario"],
        )
        groups.setdefault(key, []).append(sample)

    rows: list[dict[str, Any]] = []
    for (language, latency, method, scenario), group in sorted(groups.items()):
        base = {
            "language": language,
            "latency": latency,
            "method": method,
            "scenario": scenario,
            "collection_shape": group[0]["collection_shape"],
            "data_shape": group[0]["data_shape"],
        }
        for metric in METRICS:
            summary = summarize_values([entry[metric] for entry in group])
            for key, value in summary.items():
                base[f"{metric}_{key}"] = value
        rows.append(base)
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_samples_csv(path: Path, samples: list[dict[str, Any]]) -> None:
    if not samples:
        path.write_text("", encoding="utf-8")
        return
    headers = sorted({key for sample in samples for key in sample.keys()})
    lines = [",".join(headers)]
    for sample in samples:
        values = []
        for header in headers:
            value = sample.get(header, "")
            if isinstance(value, str):
                values.append(json.dumps(value))
            else:
                values.append(str(value))
        lines.append(",".join(values))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_summary_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Telepact Performance Summary",
        "",
        "This file is generated by `test/performance/run.py`.",
        "",
        "## Scenario summaries",
        "",
        "| Language | Latency | Method | Scenario | Req bytes mean | Resp bytes mean | Req transit p95 (ms) | Resp transit p95 (ms) |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {language} | {latency} | {method} | {scenario} | {req:.2f} | {resp:.2f} | {req_t:.3f} | {resp_t:.3f} |".format(
                language=row["language"],
                latency=row["latency"],
                method=row["method"],
                scenario=row["scenario"],
                req=row["request_size_bytes_mean"],
                resp=row["response_size_bytes_mean"],
                req_t=row["request_network_transit_ns_p95"] / 1_000_000.0,
                resp_t=row["response_network_transit_ns_p95"] / 1_000_000.0,
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def refresh_latest(latest_dir: Path, source_dir: Path) -> None:
    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    shutil.copytree(source_dir, latest_dir)


def unique_run_id() -> str:
    return uuid.uuid4().hex[:12]
