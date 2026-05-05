# Operating Boundary Guide

This page is intentionally narrow.

Telepact is a small RPC layer, not a production framework. It does not try to
teach general service operations or prescribe one enterprise rollout model. Its
job is to make the Telepact boundary explicit so your surrounding service can
attach its own auth, logging, metrics, routing, and deployment systems in the
right places.

For byte-level wiring, see the
[Transport Guide](../03-build-clients-and-servers/01-transports.md).

## 1. What Telepact owns

Telepact owns:

- schema-defined request and response shapes
- schema validation
- serialization and deserialization
- binary negotiation
- request / response semantics such as `ErrorInvalid*` and `ErrorUnknown_`
- the middleware and hook points around a validated Telepact request

Telepact does **not** own:

- gateways, meshes, or reverse proxies
- TLS, sockets, and HTTP-specific policy
- service discovery or load balancing
- rate limiting, retries, or circuit breaking
- tracing backends, metrics backends, or log pipelines
- deployment policy, rollout procedure, or incident response process

That split is the main operating model. Keep the Telepact core small, then let
your service's own production stack handle the rest.

## 2. Where cross-cutting concerns belong

Use this placement guide:

| Concern | Primary home |
| --- | --- |
| TLS, sockets, HTTP / WebSocket details, request size limits, timeouts | Transport layer or infrastructure around Telepact |
| Service discovery, load balancing, retries, circuit breaking | Caller, gateway, mesh, or other surrounding infrastructure |
| Credentials crossing from HTTP cookies, bearer tokens, or other transport state into Telepact | Transport adapter |
| Auth normalization, request ids, per-function logs, per-function metrics | Telepact middleware and hooks |
| Domain authorization and business rules | Middleware and function routes that own the data |
| Schema validation, serialization, Telepact headers, Telepact errors | Telepact runtime |

Rule of thumb:

- if it depends on network or transport details, keep it outside Telepact
- if it depends on validated Telepact headers, function names, or Telepact
  outcomes, Telepact middleware is usually the right cutpoint
- if it depends on domain data or business rules, keep it with the handlers or
  surrounding service logic

## 3. Auth, logging, and metrics

Telepact cares mainly about placement.

### Auth

Telepact's auth convention is:

- define caller-visible credential variants in `union.Auth_`
- carry them in `.auth_`
- translate transport-specific credential state into `.auth_` at the transport boundary when needed
- use `onAuth` to normalize authenticated identity into internal headers
- keep authorization decisions near the business logic that owns the resource

The Telepact-specific point is not how your organization should issue tokens or
run a gateway. It is that Telepact has one conventional in-band auth shape and
one conventional hook point once credentials cross into the Telepact request.

Use the standard auth errors consistently:

- `ErrorUnauthenticated_` for missing or invalid credentials
- `ErrorUnauthorized_` for authenticated callers who are not allowed to perform the action

For the canonical schema shape and examples, see the
[Auth Guide](../03-build-clients-and-servers/05-auth.md).

### Logging and metrics

If you want Telepact-aware logs or metrics, emit them from middleware or hooks
that can see:

- the Telepact function name
- normalized caller context
- the response outcome
- elapsed time

Transport logs still answer different questions from Telepact logs. Transport
logs describe connections and byte-level behavior; Telepact logs can describe
which Telepact function ran and how it completed.

One Telepact-specific pitfall: avoid dumping whole request or response `Message`
objects just because they are available. Even though `.auth_` is treated
carefully by Telepact, application payloads may still contain sensitive data.

### Request ids and tracing

Telepact can carry correlation data in headers, but it does not define a tracing
policy. The important Telepact point is simply to keep the ids consistent across
the transport boundary and the Telepact middleware boundary so the same request
can be correlated in both places.

## 4. Expose unique transports to CLI tooling through a proxy

If your production service speaks Telepact over a transport such as NATS, stdio,
queues, or another internal RPC boundary, the CLI tooling still works best when
it can reach a normal HTTP Telepact endpoint.

In that setup, expose a small proxy specifically for tooling and operational
access:

- keep the real Telepact server on its native transport
- expose fixed HTTP routes that map to the internal transport destinations your
  tooling needs
- forward raw Telepact request and response bytes through the proxy instead of
  re-implementing Telepact semantics there
- let `telepact fetch`, `telepact mock --http-url`, and related tooling talk to
  the proxy's HTTP surface

That keeps the transport-specific production boundary explicit while still
making Telepact tooling usable from standard developer environments.

For a runnable example, see
[`example/full-stack-proxy`](../../example/full-stack-proxy/README.md), which
shows a browser and HTTP-facing proxy forwarding Telepact bytes to an internal
NATS subject.

## 5. Compatibility and upgrades

Telepact provides `telepact compare` because schema compatibility is part of the
Telepact contract surface.

The Telepact-specific guidance is:

- treat checked-in schema as part of the released contract
- compare old and new schema when the contract changes
- keep generated bindings, schema files, and Telepact runtime versions aligned
- stage breaking changes so callers are not forced across incompatible message
  shapes all at once

For the practical Git-based workflow to compare the checked-in schema on your
branch with `origin/main` or a release tag, see
[Tooling Workflow: Compare schema versions](../03-build-clients-and-servers/04-tooling-workflow.md#compare-schema-versions).

Telepact does not prescribe the surrounding rollout procedure. Whether your
organization uses canaries, blue/green, staged regional rollout, or something
else is outside this library's scope.

## 6. Error boundary notes

Telepact keeps wire behavior and local diagnostics separate:

- schema-invalid messages return `ErrorInvalid*`
- unexpected handler or serialization failures return `ErrorUnknown_` on the wire
- local hooks and exceptions carry the details needed for debugging

That separation is intentional. It keeps the public RPC surface stable while
still giving the surrounding service a place to log or inspect failures.

See the [Runtime Error Guide](./02-runtime-errors.md) for the current local error
categories.
