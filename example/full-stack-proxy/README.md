# full-stack-proxy

A runnable Telepact example with a Python backend, a TypeScript browser frontend,
and a websocket-to-NATS proxy.

This example keeps the same API, auth flow, metrics, and Playwright coverage as
[`full-stack`](../full-stack/README.md), but moves the browser Telepact traffic to
an intermediate websocket proxy. The proxy has no Telepact code. It forwards raw
message bytes to the NATS topic named in the websocket URL, and the real Telepact
server handles the request behind that transport boundary.

## Layout

- [`api/dashboard.telepact.yaml`](./api/dashboard.telepact.yaml) - current
  checked-in Telepact schema
- [`schema-baseline/dashboard.telepact.yaml`](./schema-baseline/dashboard.telepact.yaml)
  - baseline schema snapshot for compatibility checks
- [`server/app.py`](./server/app.py) - Python HTTP adapter that serves the app,
  session endpoints, ops snapshot, and starts the NATS-backed Telepact server
- [`server/telepact_app.py`](./server/telepact_app.py) - Telepact server hooks,
  auth normalization, metrics, handlers, and NATS bridge
- [`server/run_demo.py`](./server/run_demo.py) - local supervisor that starts
  NATS, the HTTP server, and the websocket proxy for Playwright
- [`proxy/app.py`](./proxy/app.py) - websocket-to-NATS byte proxy with no
  Telepact code
- [`client/src/main.ts`](./client/src/main.ts) - Vite-powered TypeScript browser
  UI entry point that talks to the proxy over WebSocket
- [`client/src/app.html`](./client/src/app.html) - browser UI markup
- [`client/tests/e2e.spec.ts`](./client/tests/e2e.spec.ts) - Playwright end-to-end
  coverage

## Run it

```bash
make run
```

That target rebuilds the local Telepact Python and TypeScript packages, installs
browser and proxy dependencies, builds the browser app, starts a local NATS
server, and runs the Playwright end-to-end suite.

## Inspect schema compatibility

If you already have the `telepact` CLI installed, compare the current schema with
its checked-in baseline:

```bash
telepact compare --old-schema-dir ./schema-baseline --new-schema-dir ./api
```
