# Performance Harness

This harness compares Telepact and protobuf request/reply behavior over NATS using
`demo.nats.io` to include real network transit.

## Coverage

The harness runs every combination of:

- Method
  - `telepact_json`
  - `telepact_binary`
  - `telepact_packed_binary`
  - `protobuf`
  - `plain_json`
- Collection shape
  - `single`
  - `small_list`
  - `big_list`
  - `really_big_list`
- Data shape
  - `typical_data`
  - `all_strings`
  - `all_numbers`
- Programming language
  - `python`
  - `typescript`
  - `java`

Each measured sample records:

- client-side request serialization time
- serialized request size in bytes
- request network transit time
- server-side request deserialization time
- server-side response serialization time
- serialized response size in bytes
- response network transit time
- client-side response deserialization time

Warmup iterations are excluded so Telepact binary-encoding negotiation traffic does
not contaminate steady-state measurements.

## Run

```sh
cd /home/runner/work/telepact/telepact/test/performance
make run
```

Useful overrides:

```sh
make run WARMUP=5 ITERATIONS=20 NATS_URL=nats://demo.nats.io:4222
```

Outputs:

- `results/raw-<language>.json` raw per-sample measurements
- `results/latest-summary.json` aggregated statistics
- `results/latest-summary.md` markdown summary for review and docs
