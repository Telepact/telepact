# Performance Guide

This guide is about the Telepact choices that most directly affect client-side
performance.

For a runnable benchmark that measures these tradeoffs with the Python runtime,
see [`example/py-performance`](../../example/py-performance/README.md).

## 1. Measure steady-state, not the binary handshake

Telepact binary is negotiated at runtime.

That means the very first binary-enabled request may carry extra bytes while the
client and server agree on the encoding. Do not treat that cold-start exchange
as your normal steady-state cost. Measure after negotiation has completed.

Use this rule of thumb:

- for one-off or very infrequent calls, plain JSON may be good enough
- for repeated calls between the same client and server, enable binary and judge
  the steady-state path after negotiation

The Python performance harness explicitly discards handshake samples before it
reports binary metrics.

## 2. Pick the highest-leverage option first

In practice, these optimizations usually stack in this order:

1. `@select_` to avoid sending fields the client does not need
2. runtime binary to reduce repeated key overhead and binary/base64 churn
3. packed-binary-friendly response shapes for list-of-struct workloads
4. `@unsafe_` only on trusted hot paths where skipping response validation is an
   intentional tradeoff

If you only adopt one thing, start with `@select_`. Removing unused fields helps
both JSON and binary callers and improves transfer time on every network.

## 3. Guidance by client situation

### Browser or mobile UI reading only part of a large response

Prefer:

- `@select_` on every partial-read request
- binary for repeated polling or interactive refreshes

Why:

- UI surfaces often need a thin slice of a server response
- `@select_` removes unnecessary fields before they hit the wire
- on higher-latency links, byte savings translate directly into better perceived
  latency

Typical fit:

- dashboards
- detail pages
- search/autocomplete side panels
- background refreshes on mobile networks

### Service-to-service calls with repeated medium or large payloads

Prefer:

- runtime binary by default
- JSON only when you truly need human-readable transport payloads or very cold,
  low-frequency calls

Why:

- the binary negotiation cost is amortized quickly on repeated traffic
- steady-state payloads are smaller and serialization work is usually lower

Typical fit:

- internal HTTP or WebSocket RPC
- queue or socket adapters that forward raw Telepact bytes
- repeated polling between long-lived peers

### Analytics or export-style responses with many repeated rows

Prefer:

- binary
- list-of-struct response shapes when they naturally represent the data

Why:

- Telepact's packed binary path compresses repeated field names for list-of-struct
  payloads automatically
- this is usually the biggest binary win in row-heavy responses

Typical fit:

- tables
- feeds
- batched records
- history/event exports

### Trusted internal callers chasing the lowest server-side latency

Consider:

- `@unsafe_` on specific hot paths only after measuring

Why:

- it asks the server to skip response validation
- that can reduce steady-state latency for large responses
- it is a tradeoff: malformed responses are no longer blocked by the runtime

Use it when all of the following are true:

- the caller is trusted
- the handler is mature and tightly controlled
- you already measured that validation is a meaningful part of the hot path
- you are comfortable giving up Telepact's normal hard-failure protection there

Avoid it for:

- untrusted callers
- newly developed handlers
- broad default client settings

## 4. Match the optimization to the transport

### Low-latency local or same-rack links

Focus first on CPU-side wins:

- binary for repeated calls
- `@unsafe_` only if measurement proves validation cost matters

On very fast local links, RTT is already small, so byte-size savings matter less
than avoiding unnecessary serialization and validation work.

### Typical office, Wi-Fi, or regional mobile links

Focus first on payload size:

- `@select_`
- binary
- packed-friendly row responses

Here, size savings often improve both throughput and tail latency.

### Cross-country or intercontinental links

Focus on anything that removes bytes from large steady-state responses:

- `@select_`
- binary
- packed row shapes

Distance dominates the RTT floor, but smaller payloads still help once the
response is large enough or the available bandwidth is limited.

## 5. Practical recommendations

- default to JSON for the simplest cold-start integrations and debugging-first
  workflows
- switch to binary when the same client/server pair talks repeatedly
- design list-heavy result sets as arrays of structs so packed binary can help
- use `@select_` for read paths where clients only need a subset of fields
- reserve `@unsafe_` for measured, trusted, internal hot paths
- benchmark with your real payload shapes, not synthetic scalars only

## 6. What to measure in your own environment

At minimum, capture:

- steady-state request bytes
- steady-state response bytes
- serialization/deserialization time
- end-to-end request latency
- separate results for small and large payloads
- separate results for flat, string-heavy, number-heavy, and row-heavy shapes

That gives you enough evidence to decide whether the next win comes from
selection, binary, packed binary, or validation skipping.
