# Binary Serialization Guide

This guidance is based on the NATS request / reply benchmark harness under
[`test/performance`](../../test/performance/README.md) and the captured run in
[`test/performance/results/benchmark-20260511.csv`](../../test/performance/results/benchmark-20260511.csv).

That run covered:

- Python, TypeScript, and Java
- Telepact JSON, Telepact binary, Telepact packed binary, protobuf, and plain JSON
- single, small-list, big-list, and really-big-list payloads
- typical-data, all-strings, and all-numbers shapes
- close NATS (`127.0.0.1`) and far NATS (`demo.nats.io`)
- 5 warmup requests and 25 measured steady-state samples per scenario

## What the data says

### 1. Telepact binary materially cuts wire size

Across all languages and payload shapes, the average median request size was:

| Method | Average median request size |
| --- | ---: |
| Telepact JSON | 10.7 KB |
| Telepact binary | 5.0 KB |
| Telepact packed binary | 4.5 KB |
| protobuf | 3.8 KB |
| plain JSON | 11.5 KB |

So regular Telepact binary reduced average request bytes by about **52.5%**
versus Telepact JSON, with a similar **52.7%** reduction on responses.

For the `really-big-list` scenarios, the average median request size dropped
from **33.3 KB** (Telepact JSON) to **15.6 KB** (Telepact binary).

### 2. Packed binary helps large lists, but not single messages

Packed binary was not a universal win.

For `single` payloads, its average median request size was **102 B**, which was
actually larger than regular Telepact binary at **89 B**.

For list-heavy cases it helped:

- `small-list`: about **7%** smaller than regular Telepact binary
- `big-list`: about **11%** smaller
- `really-big-list`: about **11.4%** smaller

### 3. The extra packing work costs CPU time

Average median client request serialization time across all scenarios:

| Method | Avg median request serialization |
| --- | ---: |
| Telepact JSON | 0.22 ms |
| Telepact binary | 0.29 ms |
| Telepact packed binary | 0.60 ms |

Average median client response deserialization time:

| Method | Avg median response deserialization |
| --- | ---: |
| Telepact JSON | 0.16 ms |
| Telepact binary | 0.37 ms |
| Telepact packed binary | 0.59 ms |

Relative to regular Telepact binary, packed binary increased:

- request serialization by about **31%** for `single`
- by about **42%** for `small-list`
- by about **93%** for `big-list`
- by about **140%** for `really-big-list`

### 4. Binary size savings did not meaningfully lower NATS transit time here

In this harness, message transit time was mostly dominated by the broker hop and
the network path, not by payload size.

Average median request transit times:

| Latency target | Telepact JSON | Telepact binary | Telepact packed binary |
| --- | ---: | ---: | ---: |
| close NATS | 0.296 ms | 0.301 ms | 0.308 ms |
| far NATS | 32.195 ms | 32.111 ms | 32.110 ms |

The WAN case is the clearest signal: once the request crosses the public demo
NATS path, the extra ~5-6 KB saved by Telepact binary is tiny relative to a
~32 ms transit budget.

## Recommendations

### Prefer Telepact JSON when:

- requests are small
- debugging readability matters more than bandwidth
- end-to-end latency is dominated by a remote network hop

### Prefer regular Telepact binary when:

- request or response size matters
- you want a clear size reduction without the extra CPU cost of packing
- you are trying to stay farther away from transport payload limits

This is the best default binary option. It cuts bytes roughly in half versus
Telepact JSON while keeping encode / decode overhead moderate.

### Use Telepact packed binary selectively

Packed binary is best treated as a specialized option for list-heavy payloads.

Use it when all of the following are true:

- your traffic is dominated by medium or large collections
- bandwidth or message size is a real constraint
- the extra serialization CPU is acceptable

Avoid it for singleton-style calls. In this benchmark it made single-request
payloads larger than regular Telepact binary and still cost more CPU.

### Do not expect binary mode alone to fix WAN latency

The far-NATS results show that binary modes are mainly a **size and bandwidth**
tool, not a general RTT optimization. If your main problem is remote latency,
focus first on network placement, broker topology, batching strategy, or call
count reduction.

## Practical rule of thumb

- **Human-facing or low-volume RPC**: start with Telepact JSON
- **General production RPC**: use regular Telepact binary
- **Large repeated collections under size pressure**: consider packed binary, but validate CPU cost on your own traffic
