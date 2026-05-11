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
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any

from common import LATENCIES, load_json, refresh_latest, summarize_samples, write_json, write_manifest, write_samples_csv, write_summary_markdown

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
SCHEMA_DIR = ROOT / "schema"
MANIFEST_PATH = ROOT / "gen" / "manifest.json"


def _wait_for_local_nats() -> subprocess.Popen[str]:
    process = subprocess.Popen(["nats-server", "-D"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            import socket

            with socket.create_connection(("127.0.0.1", 4222), timeout=0.5):
                return process
        except OSError:
            time.sleep(0.25)
    process.terminate()
    process.wait(timeout=5)
    raise RuntimeError("local nats-server did not start in time")


def _run_worker(command: list[str], *, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--warmup-iterations", type=int, default=5)
    parser.add_argument("--measure-iterations", type=int, default=100)
    parser.add_argument("--languages", nargs="*", default=["python", "typescript", "java"])
    parser.add_argument("--latencies", nargs="*", default=["close", "far"])
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    run_dir = output_root / _timestamp()
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    (ROOT / "gen").mkdir(exist_ok=True)
    write_manifest(MANIFEST_PATH, warmup_iterations=args.warmup_iterations, measure_iterations=args.measure_iterations)

    local_nats: subprocess.Popen[str] | None = None
    if "close" in args.latencies:
        local_nats = _wait_for_local_nats()

    try:
        worker_outputs: list[dict[str, Any]] = []
        for language in args.languages:
            for latency in args.latencies:
                output_path = run_dir / f"{language}-{latency}.json"
                nats_url = LATENCIES[latency]
                if language == "python":
                    command = [
                        sys.executable,
                        str(ROOT / "python_worker.py"),
                        "--language",
                        language,
                        "--latency",
                        latency,
                        "--nats-url",
                        nats_url,
                        "--schema-dir",
                        str(SCHEMA_DIR),
                        "--manifest",
                        str(MANIFEST_PATH),
                        "--output",
                        str(output_path),
                    ]
                    _run_worker(command, cwd=ROOT)
                elif language == "typescript":
                    command = [
                        "npm",
                        "start",
                        "--",
                        "--language",
                        language,
                        "--latency",
                        latency,
                        "--nats-url",
                        nats_url,
                        "--schema-dir",
                        str(SCHEMA_DIR),
                        "--manifest",
                        str(MANIFEST_PATH),
                        "--output",
                        str(output_path),
                    ]
                    _run_worker(command, cwd=ROOT / "ts")
                else:
                    command = [
                        "mvn",
                        "-q",
                        "-s",
                        "settings.xml",
                        f"-Dexec.args=--language {language} --latency {latency} --nats-url {nats_url} --schema-dir {SCHEMA_DIR} --manifest {MANIFEST_PATH} --output {output_path}",
                        "exec:java",
                    ]
                    _run_worker(command, cwd=ROOT / "java")
                worker_outputs.extend(load_json(output_path))

        summary_rows = summarize_samples(worker_outputs)
        write_json(run_dir / "samples.json", worker_outputs)
        write_samples_csv(run_dir / "samples.csv", worker_outputs)
        write_json(run_dir / "summary.json", summary_rows)
        write_summary_markdown(run_dir / "summary.md", summary_rows)
        refresh_latest(output_root / "latest", run_dir)
    finally:
        if local_nats is not None:
            local_nats.terminate()
            local_nats.wait(timeout=5)


if __name__ == "__main__":
    main()
