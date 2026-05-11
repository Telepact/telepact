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
from datetime import datetime, timezone
from itertools import product
from math import sqrt
from pathlib import Path
import csv
import json
import statistics
from typing import Any, Iterable

LANGUAGES = ("python", "typescript", "java")
NETWORK_LATENCIES = ("close", "far")
DATA_SHAPES = ("typical", "all-strings", "all-numbers")
COLLECTION_SHAPES = ("single", "small-list", "big-list", "really-big-list", "huge-list")
METHODS = (
    "telepact-json",
    "telepact-binary",
    "telepact-packed-binary",
    "protobuf",
    "plain-json",
)
TIME_METRICS = (
    "clientRequestSerializationTimeNs",
    "requestNetworkTransitTimeNs",
    "serverRequestDeserializationTimeNs",
    "serverResponseSerializationTimeNs",
    "responseNetworkTransitTimeNs",
    "clientResponseDeserializationTimeNs",
)
SIZE_METRICS = (
    "serializedRequestSizeBytes",
    "serializedResponseSizeBytes",
)
ALL_METRICS = TIME_METRICS + SIZE_METRICS
FUNCTION_NAMES = {
    "typical": "fn.roundTripTypical",
    "all-strings": "fn.roundTripStrings",
    "all-numbers": "fn.roundTripNumbers",
}
PLAIN_FUNCTION_NAMES = {
    "typical": "roundTripTypical",
    "all-strings": "roundTripStrings",
    "all-numbers": "roundTripNumbers",
}
PROTODESC = {
    "typical": ("TypicalRequest", "TypicalResponse", "items"),
    "all-strings": ("StringsRequest", "StringsResponse", "items"),
    "all-numbers": ("NumbersRequest", "NumbersResponse", "items"),
}
COLLECTION_SIZES = {
    "single": 1,
    "small-list": 8,
    "big-list": 64,
    "really-big-list": 512,
    "huge-list": 1200,
}
NATS_REQUEST_TIMEOUT_SECONDS = 15
NATS_TIMEOUT_ADDITIONAL_RETRIES = 2
NATS_TIMEOUT_RETRY_DELAY_SECONDS = 0.25

PERFORMANCE_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = PERFORMANCE_ROOT / "schema" / "telepact"
PAYLOADS_PATH = PERFORMANCE_ROOT / "payloads" / "cases.json"
RESULTS_DIR = PERFORMANCE_ROOT / "results"
REPO_ROOT = PERFORMANCE_ROOT.parents[1]


@dataclass(frozen=True)
class Scenario:
    network_latency: str
    data_shape: str
    collection_shape: str
    method: str

    @property
    def key(self) -> str:
        return f"{self.network_latency}.{self.data_shape}.{self.collection_shape}.{self.method}"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_payloads() -> dict[str, dict[str, list[dict[str, Any]]]]:
    return json.loads(PAYLOADS_PATH.read_text())


def iter_scenarios() -> Iterable[Scenario]:
    for network_latency, data_shape, collection_shape, method in product(
        NETWORK_LATENCIES,
        DATA_SHAPES,
        COLLECTION_SHAPES,
        METHODS,
    ):
        yield Scenario(network_latency, data_shape, collection_shape, method)


def scenario_record(language: str, scenario: Scenario, iterations: int, warmup_iterations: int, samples: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "language": language,
        "networkLatency": scenario.network_latency,
        "dataShape": scenario.data_shape,
        "collectionShape": scenario.collection_shape,
        "method": scenario.method,
        "iterations": iterations,
        "warmupIterations": warmup_iterations,
        "samples": samples,
    }


def percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("percentile requires values")
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = index - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def summarize_metric(values: list[float]) -> dict[str, Any]:
    if not values:
        raise ValueError("cannot summarize empty metric list")
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    margin = 1.96 * stdev / sqrt(len(values)) if len(values) > 1 else 0.0
    mean_value = statistics.fmean(values)
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": mean_value,
        "median": statistics.median(values),
        "p95": percentile(values, 0.95),
        "p99": percentile(values, 0.99),
        "stdev": stdev,
        "confidenceInterval95": [mean_value - margin, mean_value + margin],
    }


def summarize_scenarios(raw_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summarized: list[dict[str, Any]] = []
    for record in raw_results:
        samples = record["samples"]
        metrics = {
            metric_name: summarize_metric([float(sample[metric_name]) for sample in samples])
            for metric_name in ALL_METRICS
        }
        summarized.append({
            **{k: v for k, v in record.items() if k != "samples"},
            "metrics": metrics,
        })
    return summarized


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def write_summary_csv(path: Path, summarized: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metric_columns: list[str] = []
    for metric in ALL_METRICS:
        metric_columns.extend([
            f"{metric}.mean",
            f"{metric}.median",
            f"{metric}.p95",
            f"{metric}.p99",
            f"{metric}.stdev",
            f"{metric}.min",
            f"{metric}.max",
            f"{metric}.confidenceInterval95.low",
            f"{metric}.confidenceInterval95.high",
        ])
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "language",
            "networkLatency",
            "dataShape",
            "collectionShape",
            "method",
            "iterations",
            "warmupIterations",
            *metric_columns,
        ])
        writer.writeheader()
        for row in summarized:
            record: dict[str, Any] = {
                "language": row["language"],
                "networkLatency": row["networkLatency"],
                "dataShape": row["dataShape"],
                "collectionShape": row["collectionShape"],
                "method": row["method"],
                "iterations": row["iterations"],
                "warmupIterations": row["warmupIterations"],
            }
            for metric, values in row["metrics"].items():
                record[f"{metric}.mean"] = values["mean"]
                record[f"{metric}.median"] = values["median"]
                record[f"{metric}.p95"] = values["p95"]
                record[f"{metric}.p99"] = values["p99"]
                record[f"{metric}.stdev"] = values["stdev"]
                record[f"{metric}.min"] = values["min"]
                record[f"{metric}.max"] = values["max"]
                record[f"{metric}.confidenceInterval95.low"] = values["confidenceInterval95"][0]
                record[f"{metric}.confidenceInterval95.high"] = values["confidenceInterval95"][1]
            writer.writerow(record)


def write_summary_markdown(path: Path, summarized: list[dict[str, Any]]) -> None:
    lines = [
        "# Telepact performance summary",
        "",
        "This file is generated by `test/performance`.",
        "",
        "| Language | Network | Data | Collection | Method | Req size median (B) | Resp size median (B) | Total latency median (ms) |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in summarized:
        metrics = row["metrics"]
        total_latency_ms = (
            metrics["clientRequestSerializationTimeNs"]["median"]
            + metrics["requestNetworkTransitTimeNs"]["median"]
            + metrics["serverRequestDeserializationTimeNs"]["median"]
            + metrics["serverResponseSerializationTimeNs"]["median"]
            + metrics["responseNetworkTransitTimeNs"]["median"]
            + metrics["clientResponseDeserializationTimeNs"]["median"]
        ) / 1_000_000.0
        lines.append(
            f"| {row['language']} | {row['networkLatency']} | {row['dataShape']} | {row['collectionShape']} | {row['method']} | "
            f"{metrics['serializedRequestSizeBytes']['median']:.2f} | {metrics['serializedResponseSizeBytes']['median']:.2f} | {total_latency_ms:.4f} |"
        )
    path.write_text("\n".join(lines) + "\n")
