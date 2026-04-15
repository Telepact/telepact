# Server Paths

Every Telepact server follows the same basic shape:

1. define a schema directory
2. load that schema with a Telepact runtime
3. route validated requests to function handlers
4. connect the runtime to a transport boundary

## Choose a runtime

Telepact currently ships server libraries for:

- [TypeScript](../../lib/ts/README.md)
- [Python](../../lib/py/README.md)
- [Java](../../lib/java/README.md)
- [Go](../../lib/go/README.md)

Pick the runtime that fits the service you are already building. Telepact is
transport-agnostic, so the same schema and server shape can sit behind HTTP,
WebSockets, or another IPC boundary that moves bytes.

## Minimal server path

If you want the fastest path to a running server:

- follow the [Quickstart](../quickstart.md)
- continue with [Learn by Example: Minimum server](../02-learn-by-example/08-running-our-own-server/22-minimum-server.md)
- use the runtime README for your language

## Transport adapter path

Keep the transport adapter thin.

Its job is usually just:

- receive request bytes
- call `server.process(...)`
- send response bytes back through the transport

See the [Transport Guide](../01-transport-guide.md) for concrete HTTP and WebSocket
patterns.

## Middleware and auth path

Put request-level concerns near the Telepact runtime boundary:

- auth normalization
- request ids
- logging
- metrics
- other policy checks

Start here:

- [Learn by Example: Auth](../02-learn-by-example/05-auth/18-auth.md)
- [Learn by Example: Server auth](../02-learn-by-example/08-running-our-own-server/24-server-auth.md)
- [Learn by Example: Managed auth](../02-learn-by-example/08-running-our-own-server/25-managed-auth.md)
- [Production Guide](../05-operate/01-production-guide.md)

## Production path

Before rollout, focus on:

- schema compatibility policy
- observability
- deployment topology
- exact runtime/tool versioning

Start here:

- [Production Guide](../05-operate/01-production-guide.md)
- [Runtime Error Guide](../05-operate/02-runtime-error-guide.md)
- [Versions](../05-operate/03-versions.md)
