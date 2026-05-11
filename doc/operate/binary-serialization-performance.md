# Telepact binary serialization performance

The benchmark harness under `test/performance` exists to answer one operational question: when is it worth switching a Telepact client/server path away from JSON?

The checked-in summary is `test/performance/results/latest-summary.json`.

## Important note about the checked-in sample

The harness defaults to `nats://demo.nats.io:4222`, but the sandbox used to prepare this change could not open that external connection. The checked-in summary was therefore collected with a local `NATS_URL` override against a local NATS server, while leaving the harness default pointed at `demo.nats.io` for normal use.

That means the checked-in numbers are best used to reason about serialization size and relative CPU cost. For production-style network conclusions, rerun the harness with its default transport.

## What the current data says

Three patterns are stable across Python, TypeScript, and Java in `latest-summary.json`.

1. **Telepact binary is a clear size win over Telepact JSON.**
   - For `typical_data` with `really_big_list`, Telepact binary request medians are about 42% to 46% smaller than Telepact JSON.
   - Example medians:
     - Python: `122648` bytes (`telepact_json`) vs `66883` bytes (`telepact_binary`)
     - TypeScript: `116501` vs `66885`
     - Java: `116501` vs `66883`

2. **Telepact packed binary is what gets Telepact close to protobuf on repeated collections.**
   - For `typical_data` with `really_big_list`, packed Telepact requests are within about 1% of protobuf in all three languages.
   - Example medians:
     - Python: `63829` bytes (`telepact_packed_binary`) vs `63268` (`protobuf`)
     - TypeScript: `63831` vs `63268`
     - Java: `63829` vs `63268`
   - The same pattern shows up even more strongly for `all_numbers`, where packed Telepact is effectively at protobuf size for large lists.

3. **Packed binary is most useful on larger repeated payloads, not tiny messages.**
   - For `typical_data` with `single`, packed Telepact is still much smaller than Telepact JSON, but it remains about 40% larger than protobuf because protocol metadata dominates tiny payloads.
   - For `small_list`, `big_list`, and `really_big_list`, that gap shrinks quickly and packed Telepact becomes near-protobuf in size.

## Operational guidance

Use the current data like this:

- **Stay on Telepact JSON** when payloads are small, human readability matters, or the endpoint is not bandwidth-sensitive.
- **Enable Telepact binary** when you want a broad, low-friction reduction in wire size without focusing on every last byte.
- **Enable Telepact packed binary** for list-heavy or high-volume paths where repeated field names are a meaningful part of payload size.
- **Benchmark before switching solely for latency.** The checked-in local run shows size improvements very consistently, while latency trade-offs vary more by language runtime.

## How to refresh the data

Run:

```sh
make -C test/performance run
```

Or, for local-only validation:

```sh
NATS_URL=nats://127.0.0.1:4223 make -C test/performance run
```

Then update this document against the new `test/performance/results/latest-summary.json` output.
