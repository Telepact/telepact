# Performance Harness

This harness compares Telepact and protobuf over NATS request/reply for Python,
TypeScript, and Java.

## What it measures

For each language, method, payload shape, and latency setting, the harness
captures steady-state samples for:

- client-side request serialization time
- serialized request size in bytes
- request network transit time
- server-side request deserialization time
- server-side response serialization time
- serialized response size in bytes
- response network transit time
- client-side response deserialization time

The controller warms up Telepact binary modes before recording data so the
binary-negotiation handshake is excluded from the measured samples.

## Methods

- `telepact-json`
- `telepact-binary`
- `telepact-packed-binary`
- `protobuf`
- `plain-json`

## Shapes

- collection: `single`, `small-list`, `big-list`, `really-big-list`
- data: `typical-data`, `all-strings`, `all-numbers`

The canonical payload fixtures live in `payloads/scenarios.json`. The equivalent
Telepact and protobuf schemas live in `schema/`.

## Run

```sh
cd /home/runner/work/telepact/telepact/test/performance
make run
```

Useful overrides:

- `--iterations <n>`
- `--warmup <n>`
- `--languages python typescript java`
- `--latencies close far`
- `--output-prefix <name>`

The controller writes:

- raw samples: `results/<prefix>.jsonl`
- per-scenario summaries: `results/<prefix>.csv`
- rollup markdown: `results/<prefix>.md`
