# py-http-cookie-auth

Minimal Python Telepact example that shows Telepact's recommended browser auth
flow:

- define a session credential in `union.Auth_`
- read the browser cookie at the HTTP boundary
- translate it into `@auth_`
- normalize it in `on_auth`
- reject missing or invalid sessions in middleware with `ErrorUnauthenticated_`
- reject non-admin callers in the protected route with `ErrorUnauthorized_`

Browse the files:

- [`api/auth.telepact.yaml`](./api/auth.telepact.yaml) - Telepact schema
- [`server.py`](./server.py) - server implementation
- [`test_example.py`](./test_example.py) - example test
- [`test_support.py`](./test_support.py) - test helpers
- [`Makefile`](./Makefile) - local run target

Run it:

```bash
make run
```
