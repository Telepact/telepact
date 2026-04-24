# py-ts-production

Full-stack Telepact production example with:

- a Python Telepact backend
- a browser-oriented TypeScript frontend
- transport-boundary auth extraction from an HTTP session cookie
- Telepact middleware logs, metrics, and request id propagation
- a schema compatibility check wired through `telepact compare`
- local error logging paired with stable `ErrorUnknown_` wire responses

This example is intentionally still small, but it tries to show where the
production concerns from
[`doc/04-operate/01-production-guide.md`](../../doc/04-operate/01-production-guide.md)
fit around a Telepact service boundary.

Browse the files:

- [`api/app.telepact.yaml`](./api/app.telepact.yaml) - public Telepact schema
- [`schema-baseline/app.telepact.yaml`](./schema-baseline/app.telepact.yaml) - schema baseline used by `telepact compare`
- [`server.py`](./server.py) - Python transport adapter, Telepact server, middleware, auth, logging, metrics, and static asset serving
- [`web/index.html`](./web/index.html) - browser page
- [`web/app.ts`](./web/app.ts) - TypeScript browser client
- [`test_example.py`](./test_example.py) - end-to-end verification
- [`Makefile`](./Makefile) - local build, compare, run, and serve targets

Run the verification flow:

```bash
make run
```

Run the example locally and open the printed URL in a browser:

```bash
make serve
```

Suggested browser flow:

1. sign in as viewer
2. load the dashboard
3. try the admin audit call and observe `ErrorUnauthorized_`
4. trigger the crash call and observe `ErrorUnknown_`
5. refresh observability data to inspect middleware logs, metrics, and local error details

Production-guide mapping:

- **Transport concerns**: `server.py` owns HTTP paths, cookie handling, request ids, static files, and a request size limit
- **Auth**: `union.Auth_` models the public credential shape, the HTTP boundary populates `@auth_`, and `on_auth` normalizes internal headers
- **Logging and metrics**: Telepact middleware emits per-function events and updates in-memory metrics
- **Request ids and tracing**: `X-Request-Id` is copied into `@id_` and reflected back on both the HTTP and Telepact boundaries
- **Compatibility and upgrades**: `make compare` runs `telepact compare` against the checked-in schema baseline
- **Error boundary**: the demo crash logs local details but still returns a stable `ErrorUnknown_` on the wire
