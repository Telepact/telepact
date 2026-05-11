# Performance Harness

This harness compares Telepact and protobuf request/reply performance over NATS.

## Coverage

It measures every combination of:

- method: Telepact JSON, Telepact binary, Telepact packed binary, protobuf, plain JSON
- collection shape: single, small list, big list, really big list
- data shape: typical data, all strings, all numbers
- language: Python, TypeScript, Java
- network latency: close (`nats://127.0.0.1:4222`), far (`nats://demo.nats.io:4222`)

## Metrics

Each measured sample captures:

- client-side request serialization time
- serialized request size in bytes
- request network transit time
- server-side request deserialization time
- server-side response serialization time
- serialized response size in bytes
- response network transit time
- client-side response deserialization time

Warmup iterations are excluded so Telepact binary negotiation traffic does not pollute steady-state samples.

## Usage

From the repository root:

```sh
make performance
```

Or from this directory:

```sh
make run
```

Harness output is written to `test/performance/output/<timestamp>/` and mirrored to `test/performance/output/latest/`.

Telepact schema files live under `test/performance/schema/telepact/` and protobuf schema files live under `test/performance/schema/protobuf/`.
