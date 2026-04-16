# Demos

Runnable end-to-end demos live here:

- Start with the [Quickstart](../doc/example.md) for the fastest end-to-end path.
- Use the [Transport Guide](../doc/03-build-clients-and-servers/01-transports.md) and
  [Auth Guide](../doc/03-build-clients-and-servers/05-auth.md) when you want the
  guide that explains the patterns behind these demos.

- [py-binary](./py-binary/README.md) - Minimal Python demo that shows how to verify binary negotiation
- [py-http-cookie-auth](./py-http-cookie-auth/README.md) - Minimal Python demo that shows how to pull a session cookie into `@auth_` at the HTTP boundary
- [py-links](./py-links/README.md) - Minimal Python demo that shows how to return a prepopulated function-type link
- [py-select](./py-select/README.md) - Minimal Python demo that shows how to select just the `id` field from a list of users
- [py-websocket](./py-websocket/README.md) - Minimal Python demo that shows how to use WebSocket request/reply

Recommended picks:

- Want auth? Start with [py-http-cookie-auth](./py-http-cookie-auth/README.md).
- Want browser/client transport patterns? Start with [py-websocket](./py-websocket/README.md) and the [Transport Guide](../doc/03-build-clients-and-servers/01-transports.md).
- Want opt-in protocol features? Start with [py-binary](./py-binary/README.md), [py-links](./py-links/README.md), and [py-select](./py-select/README.md).
