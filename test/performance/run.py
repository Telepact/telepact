#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path('/home/runner/work/telepact/telepact/test/performance')
SCHEMA_DIR = ROOT / 'schema'
RESULTS_DIR = ROOT / 'results'
DESCRIPTOR_SET = SCHEMA_DIR / 'performance.desc'
PYTHON_VENV = ROOT / 'python' / '.venv' / 'bin' / 'python'

LANGUAGE_COMMANDS = {
    'python': [
        str(PYTHON_VENV),
        str(ROOT / 'python' / 'runner.py'),
    ],
    'typescript': [
        'node',
        str(ROOT / 'typescript' / 'dist' / 'runner.js'),
    ],
    'java': [
        'java',
        '-cp',
        str(ROOT / 'java' / 'target' / 'classes') + ':' + str(ROOT / 'java' / 'target' / 'dependency' / '*'),
        'io.github.telepact.PerformanceRunner',
    ],
}

METRIC_KEYS = [
    'clientRequestSerializeNs',
    'requestSizeBytes',
    'requestNetworkTransitNs',
    'serverRequestDeserializeNs',
    'serverResponseSerializeNs',
    'responseSizeBytes',
    'responseNetworkTransitNs',
    'clientResponseDeserializeNs',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--nats-url', default='nats://demo.nats.io:4222')
    parser.add_argument('--warmup', type=int, default=5)
    parser.add_argument('--iterations', type=int, default=20)
    return parser.parse_args()


def ensure_descriptor_set() -> None:
    cmd = [
        str(PYTHON_VENV),
        '-m',
        'grpc_tools.protoc',
        f'-I{SCHEMA_DIR}',
        f'--descriptor_set_out={DESCRIPTOR_SET}',
        '--include_imports',
        str(SCHEMA_DIR / 'performance.proto'),
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)


def percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return float('nan')
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    index = (len(sorted_values) - 1) * p
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return float(sorted_values[lower])
    fraction = index - lower
    return float(sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * fraction)


def summarize(values: list[int | float]) -> dict[str, Any]:
    sorted_values = sorted(float(v) for v in values)
    count = len(sorted_values)
    mean = statistics.fmean(sorted_values)
    stdev = statistics.stdev(sorted_values) if count > 1 else 0.0
    stderr = stdev / math.sqrt(count) if count > 0 else 0.0
    ci_margin = 1.96 * stderr
    return {
        'count': count,
        'min': sorted_values[0],
        'max': sorted_values[-1],
        'mean': mean,
        'median': statistics.median(sorted_values),
        'stdev': stdev,
        'p95': percentile(sorted_values, 0.95),
        'p99': percentile(sorted_values, 0.99),
        'confidenceInterval95': {
            'low': mean - ci_margin,
            'high': mean + ci_margin,
        },
    }


def summarize_language(raw_path: Path) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text())
    cases: list[dict[str, Any]] = []
    for case in raw['cases']:
        metrics = {
            metric: summarize([sample[metric] for sample in case['samples']])
            for metric in METRIC_KEYS
        }
        cases.append(
            {
                'method': case['method'],
                'dataShape': case['dataShape'],
                'collectionShape': case['collectionShape'],
                'sampleCount': len(case['samples']),
                'metrics': metrics,
            }
        )
    return {
        'language': raw['language'],
        'natsUrl': raw['natsUrl'],
        'warmupIterations': raw['warmupIterations'],
        'measuredIterations': raw['measuredIterations'],
        'cases': cases,
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        '# Performance Harness Summary',
        '',
        f"- NATS URL: `{summary['natsUrl']}`",
        f"- Warmup iterations per case: {summary['warmupIterations']}",
        f"- Measured iterations per case: {summary['measuredIterations']}",
        '',
        'All Telepact binary measurements exclude warmup samples so binary encoding negotiation traffic is not counted.',
        '',
    ]
    for language_summary in summary['languages']:
        lines.extend([
            f"## {language_summary['language'].title()}",
            '',
            '| Method | Data shape | Collection shape | Req bytes mean | Resp bytes mean | Req transit p95 (ms) | Resp transit p95 (ms) | Client req serialize mean (ms) | Client resp deserialize mean (ms) |',
            '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |',
        ])
        for case in language_summary['cases']:
            req_bytes = case['metrics']['requestSizeBytes']['mean']
            resp_bytes = case['metrics']['responseSizeBytes']['mean']
            req_transit = case['metrics']['requestNetworkTransitNs']['p95'] / 1_000_000.0
            resp_transit = case['metrics']['responseNetworkTransitNs']['p95'] / 1_000_000.0
            req_ser = case['metrics']['clientRequestSerializeNs']['mean'] / 1_000_000.0
            resp_deser = case['metrics']['clientResponseDeserializeNs']['mean'] / 1_000_000.0
            lines.append(
                f"| `{case['method']}` | `{case['dataShape']}` | `{case['collectionShape']}` | {req_bytes:.2f} | {resp_bytes:.2f} | {req_transit:.3f} | {resp_transit:.3f} | {req_ser:.3f} | {resp_deser:.3f} |"
            )
        lines.append('')
    path.write_text('\n'.join(lines) + '\n')


def main() -> None:
    args = parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ensure_descriptor_set()

    raw_paths: list[Path] = []
    env = os.environ.copy()
    for language, command in LANGUAGE_COMMANDS.items():
        raw_path = RESULTS_DIR / f'raw-{language}.json'
        raw_paths.append(raw_path)
        cmd = command + [
            '--nats-url',
            args.nats_url,
            '--warmup',
            str(args.warmup),
            '--iterations',
            str(args.iterations),
            '--payloads',
            str(ROOT / 'data' / 'payloads.json'),
            '--schema-dir',
            str(SCHEMA_DIR),
            '--descriptor-set',
            str(DESCRIPTOR_SET),
            '--output',
            str(raw_path),
        ]
        subprocess.run(cmd, cwd=ROOT, env=env, check=True)

    language_summaries = [summarize_language(path) for path in raw_paths]
    summary = {
        'natsUrl': args.nats_url,
        'warmupIterations': args.warmup,
        'measuredIterations': args.iterations,
        'languages': language_summaries,
    }
    json_path = RESULTS_DIR / 'latest-summary.json'
    md_path = RESULTS_DIR / 'latest-summary.md'
    json_path.write_text(json.dumps(summary, indent=2) + '\n')
    write_markdown(summary, md_path)
    print(f'wrote {json_path}')
    print(f'wrote {md_path}')


if __name__ == '__main__':
    main()
