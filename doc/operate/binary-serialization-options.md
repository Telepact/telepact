# Binary Serialization Options Guide

Use the harness under `test/performance` to decide whether Telepact JSON, Telepact binary, or Telepact packed binary is the right tradeoff for a workload.

The harness writes its latest report to:

- `test/performance/output/latest/summary.md`
- `test/performance/output/latest/summary.json`

Those reports are the source of truth for this guidance.

## What to look at

Compare these rows for the same language, latency, and scenario:

- `telepact_json`
- `telepact_binary`
- `telepact_packed_binary`
- `protobuf`
- `plain_json`

The most useful columns are:

- `request_size_bytes_mean`
- `response_size_bytes_mean`
- `client_request_serialize_ns_mean`
- `client_response_deserialize_ns_mean`
- `server_request_deserialize_ns_mean`
- `server_response_serialize_ns_mean`
- `request_network_transit_ns_p95`
- `response_network_transit_ns_p95`

## How to interpret the data

### Telepact JSON

Prefer Telepact JSON when:

- the `single` and `small_list` rows show only small transit gains from binary modes
- operational simplicity matters more than byte reduction
- the workload is not dominated by repeated structured collections

### Telepact binary

Prefer Telepact binary when the report shows that, for the scenarios you care about:

- request and response byte sizes drop materially versus `telepact_json`
- serialization and deserialization times stay flat or improve
- network transit p95 is meaningfully lower on the `far` runs

This is usually the right first binary option to evaluate because it keeps the Telepact model intact while reducing wire size.

### Telepact packed binary

Prefer Telepact packed binary when the `big_list` and `really_big_list` rows show additional wins over plain Telepact binary, especially for:

- homogeneous list-heavy payloads
- all-number payloads
- repeated object collections where field names are a large fraction of the wire size

If the `single` or `small_list` rows are flat, that is expected. Packed binary is mainly for repeated collections, not tiny messages.

## Comparing Telepact binary modes with protobuf

Use the `protobuf` rows as the external benchmark and the `plain_json` rows as the no-Telepact baseline.

Questions to ask from the report:

- How much of protobuf's size advantage does `telepact_binary` recover versus `telepact_json`?
- Does `telepact_packed_binary` close the gap further on large repeated collections?
- Are the CPU costs acceptable in the target language?
- Are the gains large enough in the `far` runs to matter once real network latency is included?

## Recommended workflow

1. Run `make performance` from the repository root.
2. Open `test/performance/output/latest/summary.md`.
3. Find the rows for your language and data shape.
4. Compare JSON, binary, packed binary, protobuf, and plain JSON side by side.
5. Make rollout decisions from the measured rows, not from general assumptions.

Re-run the harness after schema changes, runtime upgrades, or transport changes so the report stays relevant to the current codebase.
