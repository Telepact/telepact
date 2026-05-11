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
import csv
import json
import math
import os
import secrets
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path("/home/runner/work/telepact/telepact")
HARNESS_DIR = REPO_ROOT / "test" / "performance"
RESULTS_DIR = HARNESS_DIR / "results"
PAYLOADS_PATH = HARNESS_DIR / "payloads" / "scenarios.json"
METRIC_NAMES = [
    "request_serialization_ms",
    "request_size_bytes",
    "request_network_transit_ms",
    "server_request_deserialization_ms",
    "server_response_serialization_ms",
    "response_size_bytes",
    "response_network_transit_ms",
    "response_deserialization_ms",
]
LANGUAGE_COMMANDS = {
    "python": [
        "uv",
        "run",
        "--project",
        str(HARNESS_DIR / "python"),
        "python",
        str(HARNESS_DIR / "python" / "runner.py"),
    ],
    "typescript": [
        "node",
        str(HARNESS_DIR / "typescript" / "dist" / "runner.js"),
    ],
    "java": [
        "java",
        "-cp",
        "{classpath}",
        "io.github.telepact.performance.Runner",
    ],
}


@dataclass(frozen=True)
class Scenario:
    language: str
    method: str
    collection_shape: str
    data_shape: str
    latency: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["python", "typescript", "java"],
    )
    parser.add_argument(
        "--methods",
        nargs="+",
        default=[
            "telepact-json",
            "telepact-binary",
            "telepact-packed-binary",
            "protobuf",
            "plain-json",
        ],
    )
    parser.add_argument(
        "--collection-shapes",
        nargs="+",
        default=["single", "small-list", "big-list", "really-big-list"],
    )
    parser.add_argument(
        "--data-shapes",
        nargs="+",
        default=["typical-data", "all-strings", "all-numbers"],
    )
    parser.add_argument("--latencies", nargs="+", default=["close", "far"])
    parser.add_argument("--output-prefix", default="")
    return parser.parse_args()


def ensure_results_dir() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def start_local_nats() -> subprocess.Popen[str]:
    return subprocess.Popen(
        ["nats-server", "-D", "-p", "4223"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def stop_process(process: subprocess.Popen[str] | None) -> None:
    if process is None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def scenario_iter(args: argparse.Namespace) -> Iterable[Scenario]:
    for language in args.languages:
        for method in args.methods:
            for collection_shape in args.collection_shapes:
                for data_shape in args.data_shapes:
                    for latency in args.latencies:
                        yield Scenario(
                            language=language,
                            method=method,
                            collection_shape=collection_shape,
                            data_shape=data_shape,
                            latency=latency,
                        )


def build_java_classpath() -> str:
    jar_dir = HARNESS_DIR / "java" / "target"
    app_jar = jar_dir / "telepact-performance-1.0-SNAPSHOT.jar"
    dependency_dir = jar_dir / "dependency"
    jars = [str(app_jar)] + sorted(str(path) for path in dependency_dir.glob("*.jar"))
    return ":".join(jars)


def run_scenario(
    scenario: Scenario,
    iterations: int,
    warmup: int,
    run_id: str,
    java_classpath: str,
) -> dict[str, object]:
    subject = ".".join(
        [
            "telepact",
            "performance",
            run_id,
            scenario.language,
            scenario.method,
            scenario.collection_shape,
            scenario.data_shape,
            scenario.latency,
        ]
    )
    nats_url = "nats://127.0.0.1:4223" if scenario.latency == "close" else "nats://demo.nats.io:4222"
    base_command = LANGUAGE_COMMANDS[scenario.language].copy()
    if scenario.language == "java":
        base_command[2] = java_classpath

    command = base_command + [
        "--method",
        scenario.method,
        "--collection-shape",
        scenario.collection_shape,
        "--data-shape",
        scenario.data_shape,
        "--nats-url",
        nats_url,
        "--subject",
        subject,
        "--iterations",
        str(iterations),
        "--warmup",
        str(warmup),
        "--payloads",
        str(PAYLOADS_PATH),
        "--schema-dir",
        str(HARNESS_DIR / "schema"),
    ]

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env.pop("VIRTUAL_ENV", None)
    completed = subprocess.run(
        command,
        cwd=HARNESS_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    if completed.stderr.strip():
        print(completed.stderr, file=sys.stderr)
    return json.loads(completed.stdout)


def quantile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    lower_weight = upper - index
    upper_weight = index - lower
    return ordered[lower] * lower_weight + ordered[upper] * upper_weight


def metric_summary(samples: list[dict[str, float]], metric_name: str) -> dict[str, float]:
    values = [float(sample[metric_name]) for sample in samples]
    return {
        "min": min(values),
        "max": max(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "p95": quantile(values, 0.95),
        "stdev": statistics.pstdev(values),
    }


def flatten_summary(result: dict[str, object]) -> dict[str, object]:
    row: dict[str, object] = {
        "language": result["language"],
        "method": result["method"],
        "collection_shape": result["collection_shape"],
        "data_shape": result["data_shape"],
        "network_latency": result["network_latency"],
        "warmup_iterations": result["warmup_iterations"],
        "measured_iterations": result["measured_iterations"],
    }
    samples = result["samples"]
    assert isinstance(samples, list)
    typed_samples = samples
    for metric_name in METRIC_NAMES:
        summary = metric_summary(typed_samples, metric_name)
        for key, value in summary.items():
            row[f"{metric_name}_{key}"] = round(value, 6)
    return row


def write_outputs(prefix: str, results: list[dict[str, object]]) -> None:
    raw_path = RESULTS_DIR / f"{prefix}.jsonl"
    csv_path = RESULTS_DIR / f"{prefix}.csv"
    md_path = RESULTS_DIR / f"{prefix}.md"

    with raw_path.open("w", encoding="utf-8") as raw_file:
        for result in results:
            raw_file.write(json.dumps(result, sort_keys=True))
            raw_file.write("\n")

    rows = [flatten_summary(result) for result in results]
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    by_latency: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_latency.setdefault(str(row["network_latency"]), []).append(row)

    with md_path.open("w", encoding="utf-8") as md_file:
        md_file.write("# Performance Rollup\n\n")
        md_file.write(f"- raw samples: `{raw_path.name}`\n")
        md_file.write(f"- summaries: `{csv_path.name}`\n\n")
        for latency, latency_rows in sorted(by_latency.items()):
            md_file.write(f"## {latency}\n\n")
            md_file.write("| language | method | median request size (bytes) | median response size (bytes) | median request transit (ms) | median response transit (ms) |\n")
            md_file.write("| --- | --- | ---: | ---: | ---: | ---: |\n")
            for row in latency_rows:
                md_file.write(
                    f"| {row['language']} | {row['method']} | "
                    f"{row['request_size_bytes_median']} | {row['response_size_bytes_median']} | "
                    f"{row['request_network_transit_ms_median']} | {row['response_network_transit_ms_median']} |\n"
                )
            md_file.write("\n")


def main() -> int:
    args = parse_args()
    ensure_results_dir()
    prefix = args.output_prefix or time.strftime("performance-%Y%m%d-%H%M%S")
    run_id = f"{prefix}-{secrets.token_hex(4)}"

    local_nats = None
    if "close" in args.latencies:
        local_nats = start_local_nats()
        time.sleep(2)

    try:
        java_classpath = build_java_classpath()
        results: list[dict[str, object]] = []
        for scenario in scenario_iter(args):
            print(
                "running",
                scenario.language,
                scenario.method,
                scenario.collection_shape,
                scenario.data_shape,
                scenario.latency,
                flush=True,
            )
            results.append(
                run_scenario(
                    scenario=scenario,
                    iterations=args.iterations,
                    warmup=args.warmup,
                    run_id=run_id,
                    java_classpath=java_classpath,
                )
            )
        write_outputs(prefix, results)
    finally:
        stop_process(local_nats)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
