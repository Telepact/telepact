# py-performance

Python Telepact performance harness focused on client-side tuning choices.

It runs steady-state permutations across:

- JSON vs binary
- `@pac_` packed binary mode
- `@select_`
- `@unsafe_`
- small vs big payloads
- specialized vs typical response shapes, including a large integer-only
  list-of-struct workload where `@pac_` is especially effective

The harness measures local steady-state serialization/deserialization time, wire
sizes, and round-trip timings, then derives estimated network latency from the
measured request and response byte counts. Binary handshake calls are discarded
before the steady-state metrics are reported.

It also generates:

- an inline SVG trend graph for row-heavy payload reduction vs list size
- regression-curve data for typical and integer-only row batches
- a timing tradeoff table that shows when smaller payloads cost more CPU time

Browse the files:

- [`api/performance.telepact.yaml`](./api/performance.telepact.yaml) - Telepact schema
- [`server.py`](./server.py) - in-process Telepact server used by the harness
- [`harness.py`](./harness.py) - benchmark runner and report generator
- [`test_example.py`](./test_example.py) - example test
- [`Makefile`](./Makefile) - local run target

Run it:

```bash
make run
```

Run the full benchmark directly:

```bash
python harness.py --cycles 100
```

Customize the row-trend graph inputs:

```bash
python harness.py --cycles 80 --trend-cycles 6 --trend-row-counts 8,16,32,64,128,256,384
```
