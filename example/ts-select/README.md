# ts-select

Minimal TypeScript Telepact example that shows `@select_` across result-union,
array, object, and union-payload edges.

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

The example test covers three request shapes:

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

That trims `struct.User` fields everywhere they appear in the response, including
the `users` array and the `usersById` object map.

```json
[
  {
    "@select_": {
      "->": {
        "Ok_": ["featured"]
      }
    }
  },
  {
    "fn.listUsers": {}
  }
]
```

That narrows the active result union to just the `featured` field.

```json
[
  {
    "@select_": {
      "->": {
        "Ok_": ["featured"]
      },
      "union.Highlight": {
        "Team": ["team"]
      },
      "struct.Team": ["name"]
    }
  },
  {
    "fn.listUsers": {}
  }
]
```

That trims the reachable union payload and then trims the nested `struct.Team`.
