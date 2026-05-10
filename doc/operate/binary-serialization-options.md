# Binary Serialization Options

Telepact's binary modes are most useful when payloads are list-heavy and large
enough that byte size dominates the tradeoff.

The harness in [`test/performance`](../../test/performance/README.md) captures the
relevant metrics across Python, TypeScript, and Java. A checked-in local snapshot
is available at [`test/performance/results/latest-summary.md`](../../test/performance/results/latest-summary.md).

## What the current snapshot says

The checked-in snapshot was collected with the harness against a local NATS server
(`nats://127.0.0.1:4222`) because this sandbox could not resolve `demo.nats.io` at
run time. Treat the byte-size and local CPU observations below as useful signal,
and rerun the default `demo.nats.io` harness before making claims about network
transit in your own environment.

### 1. Telepact binary materially cuts wire size versus Telepact JSON

For really big lists in the checked-in snapshot:

- Python `all_numbers` requests drop from about `91.7 KB` with `telepact_json` to
  about `32.4 KB` with `telepact_binary`
- TypeScript `typical_data` requests drop from about `101.1 KB` to about `53.6 KB`
- Java `all_numbers` requests drop from about `81.7 KB` to about `32.4 KB`

That is the clearest argument for enabling Telepact binary when a Telepact API is
moving large repeated payloads.

### 2. Packed binary usually squeezes bytes a bit further

The same snapshot shows another step down when `@pac_` is enabled:

- Python `all_numbers` really big list: `32.4 KB` → `27.4 KB`
- TypeScript `typical_data` really big list: `53.6 KB` → `47.7 KB`
- Java `all_numbers` really big list: `32.4 KB` → `27.4 KB`

So packed binary is the best Telepact option when the main goal is minimizing
wire bytes.

### 3. Packed binary is not automatically the best latency choice

The same runs also show that packed binary can cost extra local serialization or
response-deserialization CPU, especially in Python. For example, Python
`typical_data` really big list requests stay near `47.7 KB` with packed binary,
but mean client request serialization rises from roughly `1.5 ms` with regular
binary to roughly `6.6 ms` with packed binary in the current snapshot.

Use packed binary when bandwidth is scarce or payloads are very large. If local
CPU is the tighter constraint, regular Telepact binary may be the better default.

### 4. Small payloads do not justify much complexity

For single-item payloads, Telepact JSON requests are already small:

- Python `typical_data` single: about `160 B`
- TypeScript `typical_data` single: about `145 B`
- Java `typical_data` single: about `145 B`

Binary modes still help, but the absolute savings are small. For request/response
shapes like these, plain Telepact JSON is usually fine unless the endpoint is
extremely hot.

### 5. Protobuf still wins the raw-size race, but Telepact binary narrows the gap

In the same snapshot, protobuf remains smallest overall on most cases. But
Telepact binary and packed binary close much of the distance while preserving the
normal Telepact request model and schema-driven tooling.

That makes the practical recommendation:

- stay on Telepact JSON for small or moderate payloads
- move to Telepact binary for large repeated payloads when you want lower byte cost
  without changing away from Telepact
- consider packed binary only after measuring CPU vs. byte savings for your real
  traffic

## Operational use

1. Run `make performance` or `cd test/performance && make run`.
2. Review `test/performance/results/latest-summary.md` and the machine-readable
   `latest-summary.json`.
3. Re-run against the default `demo.nats.io` target before using the transit
   metrics for network-facing decisions.
