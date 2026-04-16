# py-codegen

Minimal Python Telepact example that regenerates and uses Python bindings from a local schema.

Browse the files:

- [`api/add.telepact.yaml`](./api/add.telepact.yaml) - Telepact schema
- [`gen/gen_types.py`](./gen/gen_types.py) - committed generated bindings
- [`server.py`](./server.py) - server implementation
- [`test_example.py`](./test_example.py) - example test
- [`Makefile`](./Makefile) - local run target that refreshes codegen before testing

Run it:

```bash
make run
```
