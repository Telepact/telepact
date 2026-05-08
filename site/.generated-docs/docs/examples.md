# Examples

Runnable end-to-end demos live here. The same demos are available in Python and TypeScript,
and the Telepact libraries keep their API surfaces closely aligned across languages.

- [py-binary](examples/py-binary.md) - Minimal Python demo that shows how to verify binary negotiation
- [py-codegen](examples/py-codegen.md) - Minimal Python demo that shows generated client and server bindings wired into the runtime
- [py-http-cookie-auth](examples/py-http-cookie-auth.md) - Minimal Python demo that shows how to pull a session cookie into `@auth_` at the HTTP boundary
- [py-links](examples/py-links.md) - Minimal Python demo that shows how to return a prepopulated function-type link
- [py-select](examples/py-select.md) - Minimal Python demo that shows `->`, `struct.*`, and `union.*` field selection together
- [py-simple-auth](examples/py-simple-auth.md) - Minimal Python demo that shows hard-coded auth, middleware identity logging, and unauthorized coercion
- [py-websocket](examples/py-websocket.md) - Minimal Python demo that shows how to use WebSocket request/reply

- [full-stack](examples/full-stack.md) - Python backend + browser TypeScript frontend that demonstrates Telepact auth, request IDs, logs, metrics, and Playwright e2e coverage
- [full-stack-proxy](examples/full-stack-proxy.md) - TypeScript browser frontend + Python HTTP-to-NATS proxy + Go Telepact server with Playwright e2e coverage

- [ts-binary](examples/ts-binary.md) - Minimal TypeScript demo that shows how to verify binary negotiation
- [ts-codegen](examples/ts-codegen.md) - Minimal TypeScript demo that shows generated client and server bindings wired into the runtime
- [ts-http-cookie-auth](examples/ts-http-cookie-auth.md) - Minimal TypeScript demo that shows how to pull a session cookie into `@auth_` at the HTTP boundary
- [ts-links](examples/ts-links.md) - Minimal TypeScript demo that shows how to return a prepopulated function-type link
- [ts-select](examples/ts-select.md) - Minimal TypeScript demo that shows `->`, `struct.*`, and `union.*` field selection together
- [ts-simple-auth](examples/ts-simple-auth.md) - Minimal TypeScript demo that talks to a Python Telepact server with hard-coded auth
- [ts-websocket](examples/ts-websocket.md) - Minimal TypeScript demo that shows how to use WebSocket request/reply
