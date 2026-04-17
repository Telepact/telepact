# ts-select

Minimal TypeScript Telepact example that selects just the `id` field from a list of users.

Browse the files:

- [`api/select.telepact.yaml`](./api/select.telepact.yaml) - Telepact schema
- [`server.ts`](./server.ts) - server implementation
- [`test_example.ts`](./test_example.ts) - example test
- [`test_support.ts`](./test_support.ts) - test helpers
- [`Makefile`](./Makefile) - local run target

Run it:

```bash
make run
```

The request uses the runtime-supported `@select_` shape:

```json
[
  {
    "@select_": {
      "struct.User": ["id"]
    }
  },
  {
    "fn.listUsers": {}
  }
]
```
