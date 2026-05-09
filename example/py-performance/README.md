# py-performance

Python Telepact performance harness that reports steady-state client-side metrics.

The example measures:

- serialization and deserialization time
- request, response, and total serialized payload sizes
- small vs big payload behavior
- JSON vs binary vs packed binary mode
- the effect of `@unsafe_` on big responses
- the effect of `@select_` on payload size
- estimated network latency savings derived from the measured payload sizes

Binary-mode measurements explicitly exclude the initial negotiation request that
exchanges `@enc_` / `@bin_`, so the report focuses on steady-state behavior.

Browse the files:

- [`api/performance.telepact.yaml`](./api/performance.telepact.yaml) - Telepact schema
- [`server.py`](./server.py) - in-memory Telepact server used by the harness
- [`harness.py`](./harness.py) - benchmark and reporting logic
- [`test_example.py`](./test_example.py) - executable test harness
- [`Makefile`](./Makefile) - local run target

Run it:

```bash
make run
```
