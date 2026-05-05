# py-simple-auth

Minimal Python Telepact example that starts a minimum Python server for a bakery
shift board and shows a simple auth flow with hard-coded credentials.

It demonstrates three common auth patterns:

- `on_auth` normalizes a hard-coded username/password into internal headers like
  `@employeeId` and `@station`, and throws if authentication fails
- middleware logs those normalized identity headers and catches a custom
  `Unauthorized` exception to coerce it into `ErrorUnauthorized_`
- completion of `on_auth` means identity normalization succeeded for the
  authenticated route

Hard-coded credentials used by the example:

- `lead-baker` / `opensesame` -> `@employeeId=baker-001`, `@station=oven`
- `cashier` / `knockknock` -> `@employeeId=cashier-002`, `@station=counter`
- `explode` / `boom` -> throws in `on_auth`

Browse the files:

- [`api/auth.telepact.yaml`](./api/auth.telepact.yaml) - Telepact schema
- [`server.py`](./server.py) - minimum Python Telepact server
- [`test_example.py`](./test_example.py) - Python client exercising the auth flows
- [`test_support.py`](./test_support.py) - transport helpers
- [`Makefile`](./Makefile) - local run target

Run it:

```bash
make run
```
