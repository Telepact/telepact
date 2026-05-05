# py-select

Minimal Python Telepact example that shows all three select targets in one request:

- `->` keeps only the `package` and `latestEvent` result fields
- `struct.Package` keeps only the `trackingId` field
- `union.DeliveryEvent` keeps only the `location` field on the `Dropoff` tag

Browse the files:

- [`api/select.telepact.yaml`](./api/select.telepact.yaml) - Telepact schema
- [`server.py`](./server.py) - server implementation
- [`test_example.py`](./test_example.py) - example test
- [`test_support.py`](./test_support.py) - test helpers
- [`Makefile`](./Makefile) - local run target

Run it:

```bash
make run
```

The request uses the runtime-supported `.select_` shape:

```json
[
  {
    ".select_": {
      "->": {
        "Ok_": ["package", "latestEvent"]
      },
      "struct.Package": ["trackingId"],
      "union.DeliveryEvent": {
        "Dropoff": ["location"]
      }
    }
  },
  {
    "fn.trackPackage": {}
  }
]
```
