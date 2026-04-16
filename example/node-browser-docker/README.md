# node-browser-docker

Opinionated end-to-end Telepact example for the recommended browser + Node + Docker path.

This example shows one production-style shape:

- a browser Telepact client loaded from a real HTML page
- a Node gateway that serves the browser app and exposes `/api/telepact`
- a backing Telepact service that the gateway calls over HTTP
- Docker Compose orchestration for the runnable stack

The flow demonstrates:

- checked-in Telepact schemas in `gateway-api/` and `catalog-api/`
- browser client usage from a plain browser `fetch` client
- server-to-server Telepact calls from the gateway to the backing service
- automatic binary negotiation on the gateway-to-service Telepact hop
- `@select_` to trim `struct.OrderSummary` fields in the browser response
- function links via `firstOrderDetails!`
- cookie/session auth bridging from the browser transport into `@auth_`
- CLI usage with `telepact fetch` and `telepact compare`

Run it:

```bash
make run
```

What `make run` does:

1. builds the local TypeScript Telepact package
2. builds and installs the local Telepact CLI
3. starts the Docker Compose stack during Playwright
4. drives the browser flow end to end
5. fetches the live gateway schema with the CLI and compares it to `gateway-api/`

If you want to explore the stack manually after copying `telepact.tgz` and installing the package:

```bash
docker compose up --build
```

Then open <http://127.0.0.1:8080> and click through the three buttons on the page.
