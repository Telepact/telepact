# Telepact Binary Performance Guide

This page summarizes the benchmark data produced by
[`test/performance`](../../test/performance/).

The harness ran all 450 combinations of:

- 3 languages: Python, TypeScript, Java
- 2 NATS latencies: local `nats://127.0.0.1:4222` and remote `nats://demo.nats.io:4222`
- 3 data shapes: typical, all strings, all numbers
- 5 collection shapes: single, small list, big list, really big list, huge list
- 5 methods: Telepact JSON, Telepact binary, Telepact packed binary, protobuf, plain JSON

Each combination used 6 warmup requests and then captured 60 steady-state samples,
excluding the initial Telepact binary negotiation traffic from the recorded data.
The generated artifacts live in:

- [`test/performance/results/summary.json`](../../test/performance/results/summary.json)
- [`test/performance/results/summary.csv`](../../test/performance/results/summary.csv)
- [`test/performance/results/summary.md`](../../test/performance/results/summary.md)

## 1. What the data says

### Overall median across all languages, data shapes, and collection shapes

| Network | Method | Median request size (bytes) | Median total latency (ms) |
| --- | --- | ---: | ---: |
| close | Telepact JSON | 6362.0 | 0.6818 |
| close | Telepact binary | 2538.0 | 0.8520 |
| close | Telepact packed binary | 2235.0 | 0.7551 |
| close | protobuf | 2379.0 | 0.4265 |
| close | plain JSON | 6350.0 | 0.5211 |
| far | Telepact JSON | 6362.0 | 64.9141 |
| far | Telepact binary | 2538.0 | 65.0361 |
| far | Telepact packed binary | 2235.0 | 65.0139 |
| far | protobuf | 2379.0 | 64.5925 |
| far | plain JSON | 6350.0 | 64.8628 |

The broad pattern is:

- Telepact binary cuts request size by about **60%** versus Telepact JSON.
- Telepact packed binary cuts another **12%** versus plain Telepact binary in the aggregate.
- On the **far** network, the wire-latency floor dominates everything else; all methods cluster near **65 ms**.
- On the **close** network, protobuf is still the lowest-latency option overall, while Telepact packed binary improves on plain Telepact binary for large collections but still trails protobuf and plain JSON on latency.

## 2. Representative size results

### Typical data, really big list, close network (median across Python, TypeScript, Java)

| Method | Request bytes | Response bytes | Total latency (ms) |
| --- | ---: | ---: | ---: |
| Telepact JSON | 50532 | 50503 | 1.1745 |
| Telepact binary | 20082 | 20072 | 1.9401 |
| Telepact packed binary | 17539 | 17529 | 1.7208 |
| protobuf | 19027 | 19027 | 0.5978 |
| plain JSON | 50520 | 50520 | 1.5092 |

### All-numbers data, really big list, close network (median across Python, TypeScript, Java)

| Method | Request bytes | Response bytes | Total latency (ms) |
| --- | ---: | ---: | ---: |
| Telepact JSON | 42933 | 42904 | 1.4395 |
| Telepact binary | 20739 | 20729 | 1.5164 |
| Telepact packed binary | 18196 | 18186 | 1.4330 |
| protobuf | 18354 | 18354 | 0.4476 |
| plain JSON | 42921 | 42921 | 1.3567 |

### Typical data, single item, close network (median across Python, TypeScript, Java)

| Method | Request bytes | Response bytes | Total latency (ms) |
| --- | ---: | ---: | ---: |
| Telepact JSON | 150 | 121 | 0.5009 |
| Telepact binary | 67 | 57 | 0.4609 |
| Telepact packed binary | 79 | 69 | 0.5812 |
| protobuf | 36 | 36 | 0.3845 |
| plain JSON | 138 | 138 | 0.3406 |

### All-numbers data, huge list, far network (median across Python, TypeScript, Java)

| Method | Request bytes | Response bytes | Total latency (ms) |
| --- | ---: | ---: | ---: |
| Telepact JSON | 101035 | 101006 | 68.4777 |
| Telepact binary | 48669 | 48659 | 68.1286 |
| Telepact packed binary | 42686 | 42676 | 68.0228 |
| protobuf | 43044 | 43044 | 65.2120 |
| plain JSON | 101023 | 101023 | 68.8954 |

That last table matters: packed binary is not a universal win. For small payloads it is
actually larger than regular Telepact binary, because the packing metadata costs more than
it saves.

## 3. Practical recommendations

### Use Telepact JSON by default when transport latency dominates

If your production path looks more like the remote NATS case than the localhost case,
Telepact binary choices do not move end-to-end latency much. The far-network medians stayed
between **64.59 ms and 65.04 ms** across all methods.

That means:

- pick Telepact JSON when readability, debuggability, and operational simplicity matter most
- do not expect binary mode to rescue a high-latency transport by itself

### Use Telepact binary when payload size matters

Telepact binary is the safest general-purpose size optimization in this data set.
Across the full run it cut median request size from **6362.0 B** to **2538.0 B**.
For the close-network typical really-big-list case it reduced request size from **50.5 KB**
to **20.1 KB**.

That is useful when:

- requests or responses regularly carry medium or large collections
- you care about broker bandwidth, egress cost, or queue pressure
- you want a smaller wire format without changing away from Telepact

### Use Telepact packed binary selectively, not as the blanket default

Packed binary improved size further, but its latency behavior was mixed.
Across the close-network aggregate it moved the median from **0.8520 ms** for Telepact
binary to **0.7551 ms** for packed binary, but that aggregate win came from the bigger
collections. It still regressed on small payloads.

It was most defensible when the payload was a **large repeated collection**, especially for
number-heavy data. In the close-network all-numbers really-big-list slice, packed binary
reduced request size from **20739 B** to **18196 B** and also slightly improved median total
latency from **1.5164 ms** to **1.4330 ms**.

But the same method caused large regressions in Python on very large lists, so the data says:

- use packed binary for **big homogeneous lists**
- benchmark per language before enabling it broadly
- avoid it for **single** messages and small collections
- avoid making it the default just because it is the smallest Telepact encoding

### If absolute wire efficiency is the top priority, protobuf still wins

In this harness, protobuf was the smallest or near-smallest option in every representative
slice, and it also had the best latency medians overall.

So the trade-off is straightforward:

- if you want the strongest wire-efficiency result, protobuf is still the best fit
- if you want to stay inside the Telepact runtime and protocol model, Telepact binary gives a
  meaningful size win with a much smaller conceptual shift

## 4. Recommended default policy

A reasonable data-driven policy from this run is:

1. Start with **Telepact JSON**.
2. Switch to **Telepact binary** when collection-heavy messages make size a real concern.
3. Enable **Telepact packed binary** only for measured hot paths with large repeated data,
   and validate it separately in each language runtime you ship.
4. Choose **protobuf** only when maximum wire efficiency is more important than staying in the
   Telepact format and toolchain.

That keeps the default simple while still using the binary options where this benchmark says
they are genuinely useful.
