# full-stack-proxy

A runnable Telepact example with a TypeScript browser client, a Python HTTP-to-NATS
proxy, and a Go Telepact server.

This example shows how to expose an internal NATS RPC subject through a more common
HTTP transport without putting any Telepact logic in the proxy itself. The browser
still sends Telepact request bytes and receives Telepact response bytes over fixed
HTTP routes, while the Python proxy is the only generalized component that forwards
those bytes between HTTP and the NATS subject encoded in the URL.

## Layout

- [`api/greet.telepact.yaml`](./api/greet.telepact.yaml) - Telepact schema used by the Go server and browser client
- [`client/`](./client/) - Vite-powered browser app and Playwright e2e coverage
- [`proxy/app.py`](./proxy/app.py) - Python HTTP server that serves the app and forwards raw bytes to NATS
- [`server/main.go`](./server/main.go) - Go Telepact server that listens on the configured NATS subject

## Run it

```bash
make run
```

That target rebuilds the local Go and TypeScript Telepact libraries, installs the
proxy dependencies, builds the browser app, compiles the Go server, and runs the
Playwright end-to-end suite against the full stack.
