# py-performance

Python Telepact benchmark harness that compares steady-state client-side performance knobs.

It reports:

- serialization and deserialization speed
- steady-state request/response payload sizes
- estimated network latency savings from smaller payloads
- small vs big payloads
- typical vs string-heavy vs number-heavy data shapes
- JSON vs binary vs packed binary mode
- `@unsafe_` response validation bypass
- `@select_` payload trimming

Binary-mode measurements exclude the initial negotiation exchange so the reported numbers reflect steady-state behavior.

Browse the files:

- [`api/performance.telepact.yaml`](./api/performance.telepact.yaml) - Telepact schema
- [`benchmark.py`](./benchmark.py) - benchmark harness and report generator
- [`server.py`](./server.py) - in-process Telepact server used by the harness
- [`test_example.py`](./test_example.py) - example test that runs the harness and prints the report
- [`Makefile`](./Makefile) - local run target

Run it:

```bash
make run
```
