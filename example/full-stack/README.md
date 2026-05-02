# full-stack

A runnable Telepact example with a Python backend and a TypeScript browser
frontend.

This example is intentionally broader than the minimal demos. It demonstrates the
production-boundary concerns from
[`doc/04-operate/01-production-guide.md`](../../doc/04-operate/01-production-guide.md):

- HTTP-only session cookies stay at the transport boundary and are translated into
  `@auth_`
- `on_auth` normalizes identity into internal headers such as `@userId` and `@role`
- Telepact hooks emit request IDs, per-function metrics, and structured events
  without logging whole request payloads
- authorization stays in the handler that owns the admin-only business rule
- unexpected bugs still return `ErrorUnknown_` with a client-visible `caseId`
- `schema-baseline/` gives you a checked-in schema snapshot to compare during
  contract changes

## Layout

- [`api/`](./api/) - current checked-in Telepact schema
- [`schema-baseline/`](./schema-baseline/) - baseline schema snapshot for
  compatibility checks
- [`server/`](./server/) - Python HTTP adapter and Telepact server hooks
- [`client/`](./client/) - Vite-powered TypeScript browser UI and Playwright e2e
  coverage

## Run it

```bash
make run
```

That target rebuilds the local Telepact Python and TypeScript packages, installs
browser dependencies, builds the browser app, and runs the Playwright end-to-end
suite against the Python server.

## Inspect schema compatibility

If you already have the `telepact` CLI installed, compare the current schema with
its checked-in baseline:

```bash
telepact compare --old-schema-dir ./schema-baseline --new-schema-dir ./api
```
