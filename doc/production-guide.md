# Production Guide

This guide collects the operational guidance that teams usually need before they
put a Telepact API into production.

Telepact is transport-agnostic, so production concerns split cleanly into two
layers:

- the Telepact runtime, which owns schema validation, request and response
  semantics, and serialization
- your surrounding service, which owns deployment topology, middleware,
  auth, observability, rollout controls, and incident response

For byte-level transport patterns, see the [Transport Guide](./transports.md).

## 1. Deployment topology

A common production shape is:

- one Telepact server instance inside each service process
- potentially many transport adapters funneling into the Telepact server, one per
  externally reachable surface, such as HTTP, WebSockets, NATS, or an internal
  queue consumer
- one schema directory checked into the service repository and released with the
  service
- one reverse proxy, gateway, or service mesh layer handling network policy,
  TLS termination, and traffic management outside the Telepact core
- handler code that performs auth, observability, and function delegation inside
  the Telepact server flow

A minimal HTTP deployment usually looks like this:

```text
client -> edge proxy / gateway -> transport adapter -> Telepact server -> handler -> function
```

Recommended responsibilities by layer:

- **edge proxy / gateway**
  - TLS termination
  - request size limits
  - CORS and other HTTP-specific policy when needed
  - rate limits
  - access logging
- **transport adapter**
  - map inbound bytes to the Telepact server
  - call `server.process(...)`
  - map Telepact response bytes back to the transport response
  - stay thin and focused on bytes in / bytes out
- **handler code**
  - function dispatch
  - domain validation
  - application-specific authorization checks
  - request tracing and structured logs
  - business logic

Keep the Telepact boundary small and explicit. The transport adapter should stay
thin and should not grow its own middleware stack. Put request-level policy in
the handler code that delegates messages to functions.

## 2. Compatibility policy in practice

Telepact ships a schema compatibility tool because schema evolution should be a
release gate, not a guess.

Recommended policy:

1. Treat the checked-in schema as a versioned contract.
2. Run `telepact compare` in CI for every schema change.
3. Block deployment on backwards-incompatible changes unless you are doing a
   deliberate breaking release.
4. Keep old and new services compatible long enough for staggered rollouts.

Example CI check:

```bash
telepact compare \
  --old-schema-dir path/to/schema-baseline \
  --new-schema-dir path/to/current-schema
```

If your schema baseline usually lives on `main`, you can materialize that older
version with `git` before running the compare. For a schema directory, one
practical pattern is:

```bash
rm -rf /tmp/schema-baseline
mkdir -p /tmp/schema-baseline

git archive --format=tar origin/main path/to/schema \
  | tar -x -C /tmp/schema-baseline

telepact compare \
  --old-schema-dir /tmp/schema-baseline/path/to/schema \
  --new-schema-dir path/to/schema
```

If you need a breaking change, use a staged migration:

- add a new field, function, or union tag in a backwards-compatible way
- deploy producers that can serve both old and new shapes
- deploy consumers that understand the new shape
- remove the legacy shape only after every caller has migrated

## 3. Auth and observability patterns

Telepact validates message structure, but production identity, policy, and
observability belong in the handler code. There is no special Telepact
middleware abstraction here. The normal pattern is:

```text
bytes -> Telepact server -> handler -> function
```

That handler is where you put the logic that teams would usually call
middleware: authenticate the caller, attach request metadata, emit logs and
metrics, then delegate to the target function.

### Auth

Recommended pattern:

- validate bearer tokens, sessions, or cookies before the target function runs
- translate the authenticated caller into the specific Telepact headers or
  request context your schema expects
- keep authorization decisions close to the business logic that owns the data

If credentials arrive through the transport layer, copy them into Telepact
headers while calling `server.process(...)`. For example, an HTTP adapter can
read a session cookie and pass it through `overrideHeaders`:

A runnable minimal version of this pattern lives in
[`example/ts-http-cookie-auth`](../example/ts-http-cookie-auth/README.md).

```ts
const response = await server.process(requestBytes, {
  '@auth_': { sessionToken: readSessionCookie(request) },
  '@id_': request.id,
});
```

Inside the handler, parse and validate those credentials before delegating to
the target function. An illustrative TypeScript sketch looks like this:

```ts
const server = new Server(schema, async (message) => {
  const auth = message.headers['@auth_'];
  const target = message.getBodyTarget();

  if (!auth) {
    return new Message({}, {
      ErrorUnauthenticated_: { message: 'missing credentials' },
    });
  }

  const userId = lookupUserIdFromSession(auth.sessionToken);
  if (!userId) {
    return new Message({}, {
      ErrorUnauthenticated_: { message: 'invalid credentials' },
    });
  }

  const normalizedMessage = new Message(
    { ...message.headers, '@userId': userId },
    message.body,
  );

  const startedAt = Date.now();
  try {
    return await dispatchFunction(target, normalizedMessage, auth);
  } finally {
    logger.info('telepact_request', {
      requestId: normalizedMessage.headers['@id_'],
      function: target,
      durationMs: Date.now() - startedAt,
    });
  }
}, new ServerOptions());
```

The important point is the placement: transport code stays bytes in / bytes out,
while auth and other request policy live in the handler code itself.

### Observability

At minimum, emit:

- request id / trace id
- function name
- caller identity or tenant id when available
- response outcome
- latency
- payload size when relevant

A practical logging shape is one structured event per request with stable keys
for function, duration, status, and correlation id. Emit those fields from the
handler code before or after function delegation, depending on what you need to
measure.

Do not log the entire `Message` object by default. Headers can carry
credentials, so prefer selective structured fields instead of dumping the full
request or response.

## 4. Rollout and migration guidance

For routine upgrades:

1. pin the target Telepact release explicitly
2. run unit and integration tests
3. run `telepact compare` against the last deployed schema
4. deploy one service slice or canary
5. watch error rate, latency, and request distribution by function
6. continue rollout only after the new slice is stable

For schema migrations:

1. add compatible schema first
2. deploy servers that accept or produce both shapes where needed
3. migrate clients
4. confirm traffic has drained from the legacy path
5. remove legacy schema in a later release

For incident response, keep these artifacts easy to retrieve:

- deployed schema bundle
- exact package versions from each runtime
- transport logs with request ids
- recent compatibility reports

## 5. Suggested pre-production checklist

- exact Telepact versions are pinned
- schema files are checked into the service repository
- `telepact compare` runs in CI
- auth is enforced in handler middleware and in business logic where needed
- structured logs and latency metrics exist per Telepact function without logging full `Message` objects
- request size and timeout limits are set at the transport layer
- rollout plan supports canary or staged deployment
- generated bindings are regenerated and committed during upgrades

Telepact's runtime can sit cleanly inside a production service, but the runtime
should be deployed as part of a deliberate operating model. This guide is meant
to make that model explicit.
