# Telepact Binary Performance Guide

This page summarizes the serializer benchmark data produced by
[`test/performance`](../../test/performance/).

The harness now runs 225 combinations of:

- 3 languages: Python, TypeScript, Java
- 3 data shapes: typical, all strings, all numbers
- 5 collection shapes: single, small list, big list, really big list, huge list
- 5 methods: Telepact JSON, Telepact binary, Telepact packed binary, protobuf, plain JSON

Each scenario records 20 steady-state serializer samples.
Telepact binary and Telepact packed binary use one warmup round-trip to populate the
binary encoding cache. No NATS or transport time is included: every sample measures only
request serialize, request deserialize, response serialize, and response deserialize work.

The generated artifacts live in:

- [`test/performance/results/summary.json`](../../test/performance/results/summary.json)
- [`test/performance/results/summary.csv`](../../test/performance/results/summary.csv)
- [`test/performance/results/summary.md`](../../test/performance/results/summary.md)

## 1. What the data says

### Overall median across all languages, data shapes, and collection shapes

| Method | Median request size (bytes) | Median response size (bytes) | Median total codec time (ms) |
| --- | ---: | ---: | ---: |
| Telepact JSON | 6349.0 | 6333.0 | 0.2855 |
| Telepact binary | 2528.0 | 2528.0 | 0.3284 |
| Telepact packed binary | 2225.0 | 2225.0 | 0.6117 |
| protobuf | 2379.0 | 2379.0 | 0.1486 |
| plain JSON | 6350.0 | 6350.0 | 0.2113 |

The broad pattern is:

- Telepact binary cuts median payload size by about **60%** versus Telepact JSON.
- Telepact packed binary cuts another **12%** versus plain Telepact binary.
- protobuf is still the fastest codec overall in this harness.
- Telepact packed binary is the smallest Telepact wire format, but it is not the fastest.

## 2. Representative size and codec-time results

### Typical data, really big list (median across Python, TypeScript, Java)

| Method | Request bytes | Response bytes | Total codec time (ms) |
| --- | ---: | ---: | ---: |
| Telepact JSON | 50519 | 50503 | 2.1241 |
| Telepact binary | 20072 | 20072 | 2.3609 |
| Telepact packed binary | 17529 | 17529 | 4.7284 |
| protobuf | 19027 | 19027 | 0.8051 |
| plain JSON | 50520 | 50520 | 1.2587 |

### All-numbers data, really big list (median across Python, TypeScript, Java)

| Method | Request bytes | Response bytes | Total codec time (ms) |
| --- | ---: | ---: | ---: |
| Telepact JSON | 42920 | 42904 | 1.1395 |
| Telepact binary | 20729 | 20729 | 2.3320 |
| Telepact packed binary | 18186 | 18186 | 1.5034 |
| protobuf | 18354 | 18354 | 0.6332 |
| plain JSON | 42921 | 42921 | 1.0910 |

### Typical data, single item (median across Python, TypeScript, Java)

| Method | Request bytes | Response bytes | Total codec time (ms) |
| --- | ---: | ---: | ---: |
| Telepact JSON | 137 | 121 | 0.0272 |
| Telepact binary | 57 | 57 | 0.0486 |
| Telepact packed binary | 69 | 69 | 0.0604 |
| protobuf | 36 | 36 | 0.0305 |
| plain JSON | 138 | 138 | 0.0137 |

## 3. Practical recommendations

### Use Telepact JSON when you want the simplest Telepact codec path

Telepact JSON stayed close to plain JSON on codec time while preserving the standard Telepact
message model. It remains the easiest default when payload size is not your main pressure.

### Use Telepact binary when payload size matters more than raw codec time

Telepact binary is the best general-purpose Telepact size reduction in this run.
Across the full benchmark it reduced the median request from **6349 B** to **2528 B**.
That makes it a good fit for collection-heavy messages where wire size matters.

### Use Telepact packed binary selectively for large repeated collections

Packed binary pushed size lower again, but its time cost was mixed.
It was most compelling on large number-heavy collections, where it nearly matched protobuf size
while materially beating plain Telepact binary on bytes.
It is still a poor default for small payloads.

### If raw serializer speed is the priority, protobuf still wins

protobuf delivered the best overall codec-time median in this harness and stayed smallest or
near-smallest in every representative slice.

## 4. Running fast slices

The benchmark now supports filtering by language, data shape, collection shape, and method.
That makes it easy to re-run only the slice you care about.

Examples:

```bash
cd test/performance
uv run python -m perf_harness.run \
  --languages python \
  --data-shapes all-numbers \
  --collection-shapes huge-list \
  --methods telepact-binary telepact-packed-binary
```

```bash
cd test/performance
uv run python -m perf_harness.run \
  --languages typescript java \
  --data-shapes typical \
  --collection-shapes single small-list \
  --methods telepact-json plain-json protobuf
```

Run the full benchmark with:

```bash
make -C test/performance run
```
