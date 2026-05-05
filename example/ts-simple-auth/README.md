# ts-simple-auth

Minimal TypeScript Telepact client example that starts a minimum Python bakery
server and shows a simple auth flow with hard-coded credentials.

It demonstrates the same auth boundary as the Python example:

- `on_auth` maps a hard-coded username/password from `+auth_` into normalized
  identity headers, and throws if authentication fails
- middleware logs those normalized identity headers and catches a custom
  `Unauthorized` exception to coerce it into `ErrorUnauthorized_`
- completion of `on_auth` means identity normalization succeeded for the
  authenticated route

Hard-coded credentials used by the example:

- `lead-baker` / `opensesame` -> `+employeeId=baker-001`, `+station=oven`
- `cashier` / `knockknock` -> `+employeeId=cashier-002`, `+station=counter`
- `explode` / `boom` -> throws in `on_auth`

Browse the files:

- [`api/auth.telepact.yaml`](./api/auth.telepact.yaml) - Telepact schema
- [`server.py`](./server.py) - minimum Python Telepact server
- [`test_example.ts`](./test_example.ts) - TypeScript client exercising the auth flows
- [`test_support.ts`](./test_support.ts) - Python server process and transport helpers
- [`Makefile`](./Makefile) - local run target

Run it:

```bash
make run
```
