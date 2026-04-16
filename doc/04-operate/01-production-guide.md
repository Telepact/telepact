# Production Guide

This guide collects the operational guidance that teams usually need before they
put a Telepact API into production.

Telepact is transport-agnostic, so production concerns split cleanly into two
layers:

- the Telepact runtime, which owns schema validation, request and response
  semantics, and serialization
- your surrounding service, which owns deployment topology, middleware,
  auth, observability, rollout controls, and incident response

Telepact does not provide a service mesh, a tracing backend, a metrics system, a
rate limiter, a retry coordinator, or a rollout controller. The goal in
production is to keep the Telepact boundary small and deliberate, then connect
it to those surrounding systems in predictable places.

For byte-level transport patterns, see the [Transport Guide](../03-build-clients-and-servers/01-transports.md).

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
- Telepact middleware and function routes that perform auth, observability, and
  business logic inside the Telepact server flow

A minimal HTTP deployment usually looks like this:

```text
client -> edge proxy / gateway -> transport adapter -> Telepact server -> middleware -> function route
```

Recommended responsibilities by layer:

- **edge proxy / gateway**
  - TLS termination
  - request size limits
  - transport timeouts and connection policy
  - CORS and other HTTP-specific policy when needed
  - coarse rate limits
  - canary or percentage-based traffic splitting
  - service discovery, load balancing, and health-based routing
  - access logging
- **transport adapter**
  - map inbound bytes to the Telepact server
  - forward or generate request ids and trace context at the byte boundary
  - call `server.process(...)`
  - map Telepact response bytes back to the transport response
  - preserve deadlines, cancellation, and transport-specific status mapping
  - stay thin and focused on bytes in / bytes out
  - inject credentials from the transport if applicable, e.g. cookies
- **Telepact middleware + function routes**
  - middleware for request-level policy and observability
  - domain validation
  - application-specific authorization checks
  - request tracing and structured logs
  - business logic

Keep the Telepact boundary small and explicit. The transport adapter should stay
thin and should not grow its own middleware stack. Put request-level policy in
Telepact server middleware and business logic in function routes.

Use this rule of thumb when deciding where something belongs:

- if it depends on sockets, TLS, HTTP status codes, connection pools, service
  discovery, or IP-based policy, keep it outside Telepact
- if it depends on the validated Telepact function name, headers, caller
  identity, or response outcome, put it in Telepact middleware
- if it depends on domain data or mutation semantics, keep it in the function
  route or surrounding business service

## 2. Compatibility policy in practice

Telepact ships a schema compatibility tool because schema evolution should be a
release gate, not a guess.

Recommended policy:

1. Treat the checked-in schema as a versioned contract.
2. Run `telepact compare` in CI for every schema change against the last
   deployed or otherwise supported schema baseline.
3. Fail the release if generated bindings, checked-in schema, and pinned
   Telepact runtime versions are out of sync.
4. Block deployment on backwards-incompatible changes unless you are doing a
   deliberate breaking release.
5. Keep old and new services compatible long enough for staggered rollouts.
6. Store the schema bundle and the compare report with the release artifacts so
   operators can inspect exactly what changed during an incident.

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

In practice, compatibility gates work best when they answer two separate
questions:

- **schema compatibility:** can older and newer callers still exchange valid
  Telepact messages?
- **rollout safety:** are the exact Telepact package versions, generated
  bindings, and deployed schema bundle the ones that passed validation?

Treat both as release gates.

## 3. Auth and observability patterns

Telepact validates message structure, but production identity, policy, and
observability belong in Telepact server middleware, with business logic in
function routes. The normal pattern is:

```text
bytes -> Telepact server -> middleware -> function route
```

That middleware is where you put the logic that teams would usually call
middleware: authenticate the caller, attach request metadata, emit logs and
metrics, then delegate to the target function route.

### Auth

The recommended auth model is:

- model caller credentials in `union.Auth_`
- carry them in `@auth_`
- extract transport-specific credentials into `@auth_` at the transport boundary
- use `onAuth` to normalize authenticated identity into internal request headers
- keep authorization decisions near the business logic that owns the data

The important operational point is the placement: transport code stays bytes in
/ bytes out, Telepact server hooks normalize auth and attach request metadata,
and function routes enforce business authorization.

Use the standard auth errors consistently:

- `ErrorUnauthenticated_` for missing or invalid credentials
- `ErrorUnauthorized_` for authenticated callers who are not allowed to perform the action

For the canonical schema shape, browser cookie flow, service-to-service flow,
and the explicit Telepact-vs-service ownership boundary, see the
[Auth Guide](../03-build-clients-and-servers/05-auth.md).

A runnable cookie-based example lives in
[`example/py-http-cookie-auth`](../../example/py-http-cookie-auth/README.md).

### Structured logging

Emit one structured event per Telepact request, ideally from middleware that can
see the function name, caller context, response outcome, and elapsed time.

At minimum, log stable fields for:

- request id / trace id
- function name
- caller identity or tenant id when available
- response outcome
- latency
- payload size when relevant

A practical logging shape is one structured event per request with stable keys
for function, duration, status, and correlation id. Emit those fields from the
middleware before or after function delegation, depending on what you need to
measure.

If your transport already emits access logs, keep them. They answer different
questions:

- transport logs tell you about connections, HTTP status codes, TLS, and source
  addresses
- Telepact request logs tell you which Telepact function ran, for which caller,
  with which outcome

Be careful if logging the entire `Message` object. While credentials passed
through the `@auth_` header are stripped prior to middleware and function
routes, your application data may still contain sensitive data, so prefer
selective structured fields instead of dumping the full request or response.

Good default fields are:

- service name and environment
- Telepact function name
- request id
- trace id or span id if your platform uses distributed tracing
- authenticated caller id or tenant id when allowed
- Telepact response target, such as `Ok_` or a specific error tag
- duration
- request and response byte size when useful
- rollout slice, canary marker, or deployment version

### Tracing and request ids

Telepact can carry correlation ids in headers, but it does not create a tracing
system for you. The surrounding service should define one request-id and trace
propagation policy, then the transport adapter and middleware should apply it
consistently.

Recommended pattern:

1. accept incoming request ids and trace context from the edge when present
2. generate a request id at the first trusted boundary when one is missing
3. copy that id into Telepact headers before `server.process(...)`
4. use the same id in transport logs, Telepact middleware logs, metrics, and
   error reports
5. if your transport convention allows it, echo the request id back in the
   transport response so callers can quote it in support tickets

For long-lived transports such as WebSockets, keep a per-message request id even
when the socket itself has its own connection id. Connection ids are useful for
transport debugging, but request ids are what let you trace one Telepact call
through logs and metrics.

### Metrics

Capture metrics at the same middleware boundary where you log requests.

Recommended baseline metrics:

- request count by Telepact function and outcome
- latency histograms by Telepact function
- concurrent in-flight requests if your runtime or platform exposes them
- validation/auth failures separated from domain failures when possible
- request and response byte sizes at the transport boundary

Keep labels low-cardinality. Function name, outcome class, service version, and
rollout slice are usually safe. Raw request ids, user ids, and arbitrary error
messages are not.

Telepact itself does not export metrics. Use your surrounding metrics library or
platform SDK in middleware and transport adapters.

## 4. Rollout and canary guidance

For routine upgrades:

1. pin the target Telepact release explicitly
2. run unit and integration tests
3. run `telepact compare` against the last deployed schema
4. confirm generated bindings and checked-in schema match the release candidate
5. deploy one service slice or canary
6. watch error rate, latency, validation failures, and request distribution by
   function
7. compare the canary slice to the existing slice before increasing traffic
8. continue rollout only after the new slice is stable

For canaries, make the success criteria explicit before deployment. Good default
checks are:

- no new schema-compatibility failures
- no sustained increase in validation or auth errors
- latency by Telepact function stays within expected bounds
- request volume distribution by function looks comparable to the prior slice
- rollback can restore the prior schema bundle and package versions quickly

For schema migrations:

1. add compatible schema first
2. deploy servers that accept or produce both shapes where needed
3. migrate clients
4. confirm traffic has drained from the legacy path
5. remove legacy schema in a later release

For client retries during a rollout, be conservative. Telepact validates and
routes requests, but it does not deduplicate retried writes for you. Automatic
retries belong in the caller, gateway, or mesh, and should be limited to
operations that are known to be safe or made idempotent by your application.

For incident response, keep these artifacts easy to retrieve:

- deployed schema bundle
- exact package versions from each runtime
- transport logs with request ids
- recent compatibility reports

## 5. Transport-layer responsibilities versus Telepact responsibilities

Use the following placement guide when building the surrounding service:

| Concern | Primary home | Why |
| --- | --- | --- |
| TLS termination, sockets, HTTP/WebSocket specifics | Edge proxy, gateway, mesh, or transport framework | These are transport responsibilities, not Telepact runtime responsibilities. |
| Service discovery and load balancing | Client transport, gateway, or service mesh | Instance selection happens before Telepact sees request bytes. |
| Network retries and circuit breaking | Caller, gateway, or mesh | Retry policy depends on transport failures and idempotency, which Telepact does not manage. |
| Deadlines, request size limits, and backpressure | Transport layer | These depend on connection and payload handling outside the Telepact message model. |
| Coarse rate limiting | Edge proxy, gateway, queue consumer, or mesh | IP-, token-, or connection-based admission should happen before Telepact work begins. |
| Auth normalization, request ids, per-function logs, per-function metrics | Telepact middleware and hooks | These depend on validated Telepact headers, function names, and outcomes. |
| Domain authorization and business quotas | Telepact middleware or function routes | These require authenticated caller context and domain semantics. |
| Schema validation, serialization, binary negotiation, Telepact request/response semantics | Telepact runtime | These are Telepact's core responsibilities. |

If a policy needs validated Telepact data, middleware is a good fit. If it needs
network identity, connection state, or transport routing, keep it outside
Telepact.

## 6. Practical pre-production checklist

- **Release and compatibility**
  - exact Telepact runtime, CLI, and generated binding versions are pinned
  - schema files are checked into the service repository
  - `telepact compare` runs in CI against the last deployed or otherwise
    supported baseline
  - generated bindings are regenerated and committed during upgrades
  - release artifacts include the deployed schema bundle and compare report
- **Observability**
  - every request gets a request id at the first trusted boundary
  - request ids and trace context are copied into Telepact headers and reused in
    transport logs, Telepact logs, metrics, and incident reports
  - structured logs exist per Telepact function without logging full `Message`
    objects
  - latency, request count, and failure metrics exist per Telepact function with
    bounded-cardinality labels
- **Traffic management**
  - request size, timeout, and backpressure limits are set at the transport layer
  - rate limiting is configured at the edge or another admission-control layer
  - retry policy is documented, conservative, and only automatic for safe or
    idempotent operations
  - service discovery and load balancing are handled outside Telepact
- **Runtime policy**
  - auth is enforced in Telepact middleware and in business logic where needed
  - domain authorization and quota checks are placed with the business logic that
    owns the data
  - transport adapters stay thin and do not grow a second policy stack
- **Rollout readiness**
  - rollout plan supports canary or staged deployment
  - rollback plan includes the prior schema bundle and prior package versions
  - dashboards or alerts exist for error rate, latency, and validation/auth
    failures by Telepact function

Telepact's runtime can sit cleanly inside a production service, but the runtime
should be deployed as part of a deliberate operating model. This guide is meant
to make that model explicit.
