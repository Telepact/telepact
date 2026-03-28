# Production Guide

This guide collects the operational guidance that teams usually need before they
put a Telepact API into production.

Telepact is transport-agnostic, so production concerns split cleanly into two
layers:

- the Telepact runtime, which owns schema validation, request and response
  semantics, and serialization
- your transport and service shell, which own deployment topology, auth,
  observability, rollout controls, and incident response

For byte-level transport patterns, see the [Transport Guide](./transports.md).

## 1. Deployment topology

A common production shape is:

- one Telepact server instance inside each service process
- one transport adapter per externally reachable surface, such as HTTP,
  WebSockets, NATS, or an internal queue consumer
- one schema directory checked into the service repository and released with the
  service
- one reverse proxy, gateway, or service mesh layer handling network policy,
  TLS termination, and traffic management outside the Telepact core

A minimal HTTP deployment usually looks like this:

```text
client -> edge proxy / gateway -> service transport adapter -> Telepact server -> application handler
```

Recommended responsibilities by layer:

- **edge proxy / gateway**
  - TLS termination
  - request size limits
  - coarse authn/authz policy
  - rate limits
  - access logging
- **service transport adapter**
  - map inbound bytes to the Telepact server
  - map Telepact response bytes back to the transport response
  - attach request ids, deadlines, and caller metadata
- **Telepact handler layer**
  - function dispatch
  - domain validation
  - application-specific authorization checks
  - business logic

Keep the Telepact boundary small and explicit. Do not bury transport policy deep
inside function handlers when it can live in the transport shell.

## 2. Version pinning expectations

Current public Telepact packages are prereleases. Until you adopt a stable 1.0
line, prefer exact version pinning rather than broad floating ranges.

Examples:

- Python:
  `telepact==1.0.0a224`
- CLI:
  `telepact-cli==1.0.0a224`
- TypeScript:
  `telepact@1.0.0-alpha.224`
- Java:
  `io.github.telepact:telepact:1.0.0-alpha.224`
- Go:
  `github.com/telepact/telepact/lib/go@v1.0.0-alpha.224`

Use [doc/versions.md](./versions.md) as the source of truth for published
registry versions. Repository source may move ahead of published packages
between releases.

Recommended release hygiene:

1. Pin exact Telepact versions in each service.
2. Upgrade intentionally in a branch, not incidentally during unrelated work.
3. Regenerate any generated bindings as part of the upgrade.
4. Re-run schema compatibility checks before rollout.
5. Roll forward service-by-service instead of changing every consumer at once.

## 3. Compatibility policy in practice

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

If you need a breaking change, use a staged migration:

- add a new field, function, or union tag in a backwards-compatible way
- deploy producers that can serve both old and new shapes
- deploy consumers that understand the new shape
- remove the legacy shape only after every caller has migrated

## 4. Auth and observability patterns

Telepact validates message structure, but production identity, policy, and
observability still belong in the surrounding service shell.

### Auth

Recommended pattern:

- authenticate at the transport boundary
- translate authenticated caller identity into request context or Telepact
  headers expected by your handler layer
- keep authorization decisions close to the business logic that owns the data

For HTTP services, this often means:

- bearer token or session validation in middleware
- forwarding a normalized caller identity into the Telepact handler
- rejecting unauthenticated requests before they reach business handlers

### Observability

At minimum, emit:

- request id / trace id
- function name
- caller identity or tenant id when available
- response outcome
- latency
- payload size when relevant

Recommended instrumentation points:

- before transport parsing
- immediately before `server.process(...)`
- immediately after the Telepact response is produced
- around the business handler body

A practical logging shape is one structured event per request with stable keys
for function, duration, status, and correlation id.

## 5. Rollout and migration guidance

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

## 6. Suggested pre-production checklist

- exact Telepact versions are pinned
- schema files are checked into the service repository
- `telepact compare` runs in CI
- auth is enforced at the transport boundary and in business logic where needed
- structured logs and latency metrics exist per Telepact function
- request size and timeout limits are set at the transport layer
- rollout plan supports canary or staged deployment
- generated bindings are regenerated and committed during upgrades

Telepact's runtime can sit cleanly inside a production service, but the runtime
should be deployed as part of a deliberate operating model. This guide is meant
to make that model explicit.
