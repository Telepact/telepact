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
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
from typing import Sequence

from .common import LANGUAGES, PERFORMANCE_ROOT, RESULTS_DIR, summarize_scenarios, utc_now_iso, write_json, write_summary_csv, write_summary_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=60)
    parser.add_argument("--warmup-iterations", type=int, default=6)
    parser.add_argument("--local-nats-url", default="nats://127.0.0.1:4222")
    parser.add_argument("--remote-nats-url", default="nats://demo.nats.io:4222")
    parser.add_argument("--languages", nargs="*", default=list(LANGUAGES), choices=list(LANGUAGES))
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR)
    return parser.parse_args()


def start_local_nats() -> subprocess.Popen[str]:
    return subprocess.Popen(
        ["nats-server", "-p", "4222"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        text=True,
    )


def run_command(command: Sequence[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def worker_command(language: str, args: argparse.Namespace, output_path: Path) -> tuple[list[str], Path]:
    base_args = [
        "--iterations", str(args.iterations),
        "--warmup-iterations", str(args.warmup_iterations),
        "--local-nats-url", args.local_nats_url,
        "--remote-nats-url", args.remote_nats_url,
        "--output", str(output_path),
    ]
    if language == "python":
        return [str(PERFORMANCE_ROOT / ".venv" / "bin" / "python"), "-m", "perf_harness.worker_python", *base_args], PERFORMANCE_ROOT
    if language == "typescript":
        return ["npm", "run", "benchmark", "--", *base_args], PERFORMANCE_ROOT / "ts"
    if language == "java":
        joined = " ".join(shlex.quote(part) for part in base_args)
        return ["mvn", "-q", "-s", "settings.xml", f"-Dexec.args={joined}", "exec:java"], PERFORMANCE_ROOT / "java"
    raise ValueError(language)


def main() -> None:
    args = parse_args()
    output_dir: Path = args.output_dir
    raw_dir = output_dir / "raw"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    nats_process = start_local_nats()
    try:
        raw_paths: list[Path] = []
        for language in args.languages:
            raw_output = raw_dir / f"{language}.json"
            command, cwd = worker_command(language, args, raw_output)
            run_command(command, cwd)
            raw_paths.append(raw_output)

        combined_raw: list[dict[str, object]] = []
        for raw_path in raw_paths:
            combined_raw.extend(json.loads(raw_path.read_text())["scenarios"])

        summarized = summarize_scenarios(combined_raw)
        metadata = {
            "generatedAt": utc_now_iso(),
            "iterations": args.iterations,
            "warmupIterations": args.warmup_iterations,
            "localNatsUrl": args.local_nats_url,
            "remoteNatsUrl": args.remote_nats_url,
            "languages": args.languages,
        }
        write_json(output_dir / "raw-results.json", {"metadata": metadata, "scenarios": combined_raw})
        write_json(output_dir / "summary.json", {"metadata": metadata, "scenarios": summarized})
        write_summary_csv(output_dir / "summary.csv", summarized)
        write_summary_markdown(output_dir / "summary.md", summarized)
    finally:
        nats_process.send_signal(signal.SIGTERM)
        nats_process.wait(timeout=20)


if __name__ == "__main__":
    main()
