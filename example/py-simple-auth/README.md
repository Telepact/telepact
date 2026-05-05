# py-simple-auth

Minimal Python Telepact example that starts a minimal Python Telepact server and
matches hard-coded credentials sent in `@auth_`.

- define a credential shape in `union.Auth_`
- match hard-coded credentials in `on_auth`
- reject missing or invalid identities in middleware with `ErrorUnauthenticated_`
- reject non-admin callers in the protected route with `ErrorUnauthorized_`

Browse the files:

- [`api/auth.telepact.yaml`](./api/auth.telepact.yaml) - Telepact schema
- [`server.py`](./server.py) - minimum Python server implementation
- [`test_example.py`](./test_example.py) - Python client example test
- [`test_support.py`](./test_support.py) - test helpers
- [`Makefile`](./Makefile) - local run target

Run it:

```bash
make run
```
