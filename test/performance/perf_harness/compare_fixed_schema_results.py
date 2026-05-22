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
from statistics import fmean


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    return parser.parse_args()


def load_results(path: Path) -> dict[tuple[str, str], dict[str, object]]:
    rows = json.loads(path.read_text())["results"]
    return {
        (row["collectionShape"], row["method"]): row
        for row in rows
    }


def main() -> None:
    args = parse_args()
    baseline = load_results(args.baseline)
    candidate = load_results(args.candidate)

    rows: list[dict[str, object]] = []
    for key in sorted(baseline):
        baseline_row = baseline[key]
        candidate_row = candidate[key]
        baseline_ns = float(baseline_row["medianTotalLatencyNs"])
        candidate_ns = float(candidate_row["medianTotalLatencyNs"])
        rows.append({
            "collectionShape": key[0],
            "method": key[1],
            "baselineMedianMs": baseline_ns / 1_000_000.0,
            "candidateMedianMs": candidate_ns / 1_000_000.0,
            "gainPct": ((baseline_ns - candidate_ns) / baseline_ns) * 100.0,
            "requestSizeBytes": candidate_row["requestSizeBytes"],
            "responseSizeBytes": candidate_row["responseSizeBytes"],
        })

    summary: dict[str, dict[str, object]] = {}
    for method in sorted({row["method"] for row in rows}):
        method_rows = [row for row in rows if row["method"] == method]
        avg_baseline = fmean(float(row["baselineMedianMs"]) for row in method_rows)
        avg_candidate = fmean(float(row["candidateMedianMs"]) for row in method_rows)
        summary[method] = {
            "avgBaselineMedianMs": avg_baseline,
            "avgCandidateMedianMs": avg_candidate,
            "avgGainPct": ((avg_baseline - avg_candidate) / avg_baseline) * 100.0,
        }

    print(json.dumps({"rows": rows, "summary": summary}, indent=2))


if __name__ == "__main__":
    main()