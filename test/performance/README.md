# Performance harness

This harness compares Telepact against protobuf and plain JSON across Python, TypeScript, and Java.

## What it covers

Each language runs all combinations of:

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

The harness records these steady-state metrics for every sample:

- client request serialization time
- request size in bytes
- request network transit time
- server request deserialization time
- server response serialization time
- response size in bytes
- response network transit time
- client response deserialization time
- full round-trip time

## Transport

By default the harness targets `nats://demo.nats.io:4222`.

For local validation you can override the transport endpoint with `NATS_URL`, for example:

```sh
NATS_URL=nats://127.0.0.1:4223 make -C test/performance run
```

## Commands

Prepare all language environments:

```sh
make -C test/performance prepare
```

Run the full harness:

```sh
make -C test/performance run
```

## Output

The runner writes machine-readable output to `test/performance/results/`:

- `latest-summary.json` - checked-in summary statistics by case
- `latest-raw.json` - full raw samples from a run
- `<language>-raw.json` - per-language raw samples from a run

## Fairness rules in this harness

- Telepact, protobuf, and plain JSON all use the same canned payload definitions from `config/payloads.json`.
- Telepact and protobuf schemas describe the same fields and repeated structures.
- Telepact binary warmup requests are discarded so handshake traffic does not contaminate steady-state samples.
- The same NATS request/reply flow is used for every method.
