# py-codegen

Minimal Python Telepact example that shows both the generated client and the
generated server bindings wired into the runtime library.

Browse the files:

- [`api/greet.telepact.yaml`](./api/greet.telepact.yaml) - Telepact schema
- [`gen/gen_types.py`](./gen/gen_types.py) - committed generated bindings
- [`server.py`](./server.py) - generated server handler wired into Telepact
- [`test_example.py`](./test_example.py) - generated client wired into Telepact
- [`Makefile`](./Makefile) - local run target, including codegen

Run it:

```bash
make run
```
