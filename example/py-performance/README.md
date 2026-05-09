# py-performance

Python Telepact performance harness focused on client-side tuning choices.

It runs steady-state permutations across:

- JSON vs binary
- automatic packed-binary responses for list-of-struct workloads
- `@select_`
- `@unsafe_`
- small vs big payloads
- specialized vs typical response shapes

The harness measures local steady-state serialization/deserialization time, wire
sizes, and round-trip timings, then derives estimated network latency from the
measured request and response byte counts. Binary handshake calls are discarded
before the steady-state metrics are reported.

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
