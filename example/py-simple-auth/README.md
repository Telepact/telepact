# py-simple-auth

Minimal Python Telepact example that starts a minimum Python server and shows a
simple auth flow with hard-coded credentials.

It demonstrates three common auth patterns:

- `on_auth` normalizes a hard-coded username/password into internal headers like
  `@userId` and `@role`
- middleware logs those normalized identity headers and catches a custom
  `Unauthorized` exception to coerce it into `ErrorUnauthorized_`
- any exception thrown by `on_auth` becomes `ErrorUnauthenticated_` on the client

Hard-coded credentials used by the example:

- `admin` / `swordfish` -> `@userId=user-123`, `@role=admin`
- `viewer` / `opensesame` -> `@userId=user-456`, `@role=viewer`
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
