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
import shlex
import shutil
import subprocess
from typing import Sequence

from .common import (
    COLLECTION_SHAPES,
    DATA_SHAPES,
    LANGUAGES,
    METHODS,
    PERFORMANCE_ROOT,
    RESULTS_DIR,
    summarize_scenarios,
    utc_now_iso,
    write_json,
    write_summary_csv,
    write_summary_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--warmup-iterations", type=int, default=1)
    parser.add_argument("--languages", nargs="*", default=list(LANGUAGES), choices=list(LANGUAGES))
    parser.add_argument("--data-shapes", nargs="*", default=list(DATA_SHAPES), choices=list(DATA_SHAPES))
    parser.add_argument("--collection-shapes", nargs="*", default=list(COLLECTION_SHAPES), choices=list(COLLECTION_SHAPES))
    parser.add_argument("--methods", nargs="*", default=list(METHODS), choices=list(METHODS))
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR)
    return parser.parse_args()


def run_command(command: Sequence[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def worker_command(language: str, args: argparse.Namespace, output_path: Path) -> tuple[list[str], Path]:
    methods = args.methods
    if language == "go":
        methods = [method for method in args.methods if method != "protobuf"]
        if not methods:
            raise ValueError("go performance worker does not support protobuf")

    base_args = [
        "--iterations", str(args.iterations),
        "--warmup-iterations", str(args.warmup_iterations),
        "--data-shapes", ",".join(args.data_shapes),
        "--collection-shapes", ",".join(args.collection_shapes),
        "--methods", ",".join(methods),
        "--output", str(output_path),
    ]
    if language == "python":
        return [str(PERFORMANCE_ROOT / ".venv" / "bin" / "python"), "-m", "perf_harness.worker_python", *base_args], PERFORMANCE_ROOT
    if language == "typescript":
        return ["npm", "run", "benchmark", "--", *base_args], PERFORMANCE_ROOT / "ts"
    if language == "java":
        joined = " ".join(shlex.quote(part) for part in base_args)
        return ["mvn", "-q", "-s", "settings.xml", f"-Dexec.args={joined}", "exec:java"], PERFORMANCE_ROOT / "java"
    if language == "go":
        return ["./bin/telepact-performance-go", *base_args], PERFORMANCE_ROOT / "go"
    raise ValueError(language)


def main() -> None:
    args = parse_args()
    output_dir: Path = args.output_dir
    raw_dir = output_dir / "raw"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

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
        "languages": args.languages,
        "dataShapes": args.data_shapes,
        "collectionShapes": args.collection_shapes,
        "methods": args.methods,
    }
    write_json(output_dir / "raw-results.json", {"metadata": metadata, "scenarios": combined_raw})
    write_json(output_dir / "summary.json", {"metadata": metadata, "scenarios": summarized})
    write_summary_csv(output_dir / "summary.csv", summarized)
    write_summary_markdown(output_dir / "summary.md", summarized)


if __name__ == "__main__":
    main()
