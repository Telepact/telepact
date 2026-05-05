# Demos

Runnable end-to-end demos live here. The same demos are available in Python and TypeScript,
and the Telepact libraries keep their API surfaces closely aligned across languages.

- [py-binary](./py-binary/README.md) - Minimal Python demo that shows how to verify binary negotiation
- [py-codegen](./py-codegen/README.md) - Minimal Python demo that shows generated client and server bindings wired into the runtime
- [py-http-cookie-auth](./py-http-cookie-auth/README.md) - Minimal Python demo that shows how to pull a session cookie into `@auth_`, reject missing auth in middleware, and reject non-admin users in the route that owns the policy
- [py-links](./py-links/README.md) - Minimal Python demo that shows how to return a prepopulated function-type link
- [py-select](./py-select/README.md) - Minimal Python demo that shows `->`, `struct.*`, and `union.*` field selection together
- [py-simple-auth](./py-simple-auth/README.md) - Minimal Python demo that shows a Python Telepact server matching hard-coded credentials from `@auth_`
- [py-websocket](./py-websocket/README.md) - Minimal Python demo that shows how to use WebSocket request/reply

- [full-stack](./full-stack/README.md) - Python backend + browser TypeScript frontend that demonstrates Telepact auth, request IDs, logs, metrics, and Playwright e2e coverage
- [full-stack-proxy](./full-stack-proxy/README.md) - TypeScript browser frontend + Python HTTP-to-NATS proxy + Go Telepact server with Playwright e2e coverage

- [ts-binary](./ts-binary/README.md) - Minimal TypeScript demo that shows how to verify binary negotiation
- [ts-codegen](./ts-codegen/README.md) - Minimal TypeScript demo that shows generated client and server bindings wired into the runtime
- [ts-http-cookie-auth](./ts-http-cookie-auth/README.md) - Minimal TypeScript demo that shows how to pull a session cookie into `@auth_`, reject missing auth in middleware, and reject non-admin users in the route that owns the policy
- [ts-links](./ts-links/README.md) - Minimal TypeScript demo that shows how to return a prepopulated function-type link
- [ts-select](./ts-select/README.md) - Minimal TypeScript demo that shows `->`, `struct.*`, and `union.*` field selection together
- [ts-simple-auth](./ts-simple-auth/README.md) - Minimal TypeScript demo that shows a TypeScript client calling a Python Telepact server with hard-coded credentials in `@auth_`
- [ts-websocket](./ts-websocket/README.md) - Minimal TypeScript demo that shows how to use WebSocket request/reply
