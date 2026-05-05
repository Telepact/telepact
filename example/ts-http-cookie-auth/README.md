# ts-http-cookie-auth

Minimal TypeScript Telepact example that shows Telepact's recommended browser auth
flow:

- define a session credential in `union.Auth_`
- read the browser cookie at the HTTP boundary
- translate it into `.auth_`
- normalize it in `on_auth`

Browse the files:

- [`api/auth.telepact.yaml`](./api/auth.telepact.yaml) - Telepact schema
- [`server.ts`](./server.ts) - server implementation
- [`test_example.ts`](./test_example.ts) - example test
- [`test_support.ts`](./test_support.ts) - test helpers
- [`Makefile`](./Makefile) - local run target

Run it:

```bash
make run
```
