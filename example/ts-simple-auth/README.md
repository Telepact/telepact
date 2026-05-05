# ts-simple-auth

Minimal TypeScript Telepact example that starts a minimum Python Telepact server
and calls it with hard-coded credentials in `@auth_`.

- define a credential shape in `union.Auth_`
- match hard-coded credentials in the Python server's `on_auth`
- reject missing or invalid identities in middleware with `ErrorUnauthenticated_`
- reject non-admin callers in the protected route with `ErrorUnauthorized_`

Browse the files:

- [`api/auth.telepact.yaml`](./api/auth.telepact.yaml) - Telepact schema
- [`server.py`](./server.py) - minimum Python server implementation
- [`test_example.ts`](./test_example.ts) - TypeScript client example test
- [`test_support.ts`](./test_support.ts) - Python server process helpers
- [`Makefile`](./Makefile) - local run target

Run it:

```bash
make run
```
