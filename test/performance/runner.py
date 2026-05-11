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

import json
import math
import os
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path("/home/runner/work/telepact/telepact/test/performance")
RESULTS_DIR = ROOT / "results"
CONFIG_PATH = ROOT / "config" / "benchmark-config.json"
LANGUAGES = {
    "python": {
        "cwd": ROOT / "python",
        "command": lambda output_path: ["uv", "run", "python", "perf/main.py", "--output", str(output_path)],
    },
    "typescript": {
        "cwd": ROOT / "typescript",
        "command": lambda output_path: ["node", "dist/benchmark.js", "--output", str(output_path)],
    },
    "java": {
        "cwd": ROOT / "java",
        "command": lambda output_path: [
            "mvn",
            "-q",
            "-DskipTests",
            f"-Dexec.args=--output {output_path}",
            "exec:java",
            "-s",
            "settings.xml",
        ],
    },
}
METRIC_NAMES = [
    "client_request_serialize_ns",
    "request_size_bytes",
    "request_network_transit_ns",
    "server_request_deserialize_ns",
    "server_response_serialize_ns",
    "response_size_bytes",
    "response_network_transit_ns",
    "client_response_deserialize_ns",
    "round_trip_ns",
]


def quantile(sorted_values: list[float], fraction: float) -> float:
    if not sorted_values:
        raise ValueError("quantile requires data")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * fraction
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return sorted_values[lower_index]
    weight = position - lower_index
    return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight



def summarize_metric(values: list[float]) -> dict[str, Any]:
    ordered = sorted(values)
    mean = statistics.fmean(values)
    median = statistics.median(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    stderr = stdev / math.sqrt(len(values)) if len(values) > 1 else 0.0
    confidence_delta = 1.96 * stderr
    return {
        "count": len(values),
        "min": ordered[0],
        "max": ordered[-1],
        "mean": mean,
        "median": median,
        "p95": quantile(ordered, 0.95),
        "stdev": stdev,
        "ci95_low": mean - confidence_delta,
        "ci95_high": mean + confidence_delta,
    }



def build_summary(raw: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    summarized_cases = []
    for case in raw:
        samples = case["samples"]
        metrics = {
            metric_name: summarize_metric([float(sample[metric_name]) for sample in samples])
            for metric_name in METRIC_NAMES
        }
        summarized_cases.append(
            {
                "language": case["language"],
                "method": case["method"],
                "data_shape": case["data_shape"],
                "collection_shape": case["collection_shape"],
                "sample_count": len(samples),
                "metrics": metrics,
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "nats_url": config["natsUrl"],
        "case_count": len(summarized_cases),
        "cases": summarized_cases,
    }



def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    config = json.loads(CONFIG_PATH.read_text())
    effective_nats_url = os.environ.get("NATS_URL", config["natsUrl"])
    raw_cases: list[dict[str, Any]] = []

    for language, meta in LANGUAGES.items():
        output_path = RESULTS_DIR / f"{language}-raw.json"
        command = meta["command"](output_path)
        subprocess.run(command, cwd=meta["cwd"], check=True)
        language_payload = json.loads(output_path.read_text())
        raw_cases.extend(language_payload["cases"])

    raw_report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "nats_url": effective_nats_url,
        "cases": raw_cases,
    }
    (RESULTS_DIR / "latest-raw.json").write_text(json.dumps(raw_report, indent=2) + "\n")

    config_with_effective_url = dict(config)
    config_with_effective_url["natsUrl"] = effective_nats_url
    summary = build_summary(raw_cases, config_with_effective_url)
    (RESULTS_DIR / "latest-summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
