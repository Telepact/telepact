# Auth Guide

This is Telepact's recommended auth path.

The canonical model is:

1. define every client-visible credential shape in `union.Auth_`
2. carry those credentials in `@auth_`
3. use the transport adapter to extract transport-specific credentials into `@auth_` when needed
4. use `onAuth` to validate `@auth_` and normalize it into internal request headers such as `@userId`, `@tenantId`, or `@scopes`
5. enforce authorization in middleware and function routes
6. return `ErrorUnauthenticated_` or `ErrorUnauthorized_` for auth failures

This keeps Telepact's auth surface small and explicit while leaving credential
issuance, cookie policy, token minting, and gateway behavior to the surrounding
service.

## What Telepact owns vs what your service owns

Telepact owns:

- the schema shape for `union.Auth_`
- the conventional `@auth_` request header
- the standard `ErrorUnauthenticated_` and `ErrorUnauthorized_` error shapes
- validation of schema-defined auth payloads
- the `onAuth` hook and middleware path where normalized request headers can be attached

Your surrounding service owns:

- how credentials arrive over HTTP, WebSockets, NATS, queues, or other transports
- bearer token verification, session lookup, API key lookup, mTLS identity extraction, and similar checks
- cookie issuance, cookie flags, CSRF protection, token refresh, logout, revocation, and secret management
- authorization policy decisions tied to business data and deployment-specific infrastructure

Telepact is transport-agnostic. It does not define HTTP auth middleware, cookie
settings, OAuth flows, or gateway behavior. It gives you one canonical in-band
message shape once credentials cross into the Telepact server boundary.

## Canonical schema shape

Define auth credentials in `union.Auth_`:

```yaml
- union.Auth_:
    - Session:
        token: string
    - Bearer:
        token: string
```

When `union.Auth_` exists, Telepact adds these standard definitions:

```yaml
- headers.Auth_:
    "@auth_": "union.Auth_"

- errors.Auth_:
    - ErrorUnauthenticated_:
        message!: string
    - ErrorUnauthorized_:
        message!: string
```

Recommended schema rule:

- put client-visible credential variants in `union.Auth_`
- keep normalized identity headers such as `@userId` or `@tenantId` out of the public schema unless clients are meant to send or inspect them directly

`union.Auth_` is the canonical public auth contract. Avoid inventing a second
public auth header when `@auth_` already represents the caller credentials.

## `@auth_`

`@auth_` is the canonical place for credentials inside a Telepact request.

Two common ways it gets populated:

- a Telepact-aware client sends `@auth_` directly
- the transport adapter extracts credentials from transport-specific state and writes `@auth_` before calling `server.process(...)`

Telepact runs `onAuth` only when `@auth_` is present. For protected calls, make
sure the caller or the transport adapter provides it.

## Auth error shapes

Use the standard errors consistently:

- `ErrorUnauthenticated_`: credentials were missing, malformed, expired, revoked, or otherwise not accepted
- `ErrorUnauthorized_`: the caller was authenticated, but is not allowed to perform the requested action

That split keeps auth failures predictable across services and across language
implementations.

## Transport-layer credential extraction

Transport code should stay thin. Its auth job is only to translate transport
state into the canonical Telepact auth shape.

Examples:

- HTTP cookie -> `@auth_ = {"Session": {"token": ...}}`
- HTTP `Authorization: Bearer ...` -> `@auth_ = {"Bearer": {"token": ...}}`
- gateway-verified service credential -> `@auth_ = {"Bearer": {"token": ...}}` or another `union.Auth_` variant

The transport adapter should not grow its own business authorization model. Its
role is extraction and translation.

## Normalization inside the Telepact server

Inside the server:

1. `onAuth` receives headers, including `@auth_`
2. `onAuth` validates or resolves the credential
3. `onAuth` returns normalized internal headers
4. middleware and function routes use those normalized headers for policy and business logic

Typical normalized headers are internal values like:

- `@userId`
- `@tenantId`
- `@role`
- `@scopes`

Keep these normalized headers service-specific. They are usually internal
server-to-handler data, not public client contract.

## Recommended browser / session-cookie flow

For browser sessions:

1. the browser sends its session cookie over HTTP
2. the HTTP adapter reads the cookie
3. the adapter writes the canonical `@auth_` value
4. `onAuth` looks up the session and returns normalized identity headers
5. handlers authorize with those normalized headers

This is the recommended cookie pattern because the browser does not need to
handcraft `@auth_`, while the Telepact server still receives one canonical auth
shape internally.

See:

- [Learn by Example: Managed auth](../01-learn-by-example/08-running-our-own-server/25-managed-auth.md)
- [`site/example/py-http-cookie-auth`](../../site/example/py-http-cookie-auth/README.md)

## Recommended service-to-service flow

For service-to-service calls, prefer explicit `@auth_` whenever the caller is
already constructing Telepact messages.

That usually means:

1. the calling service obtains a bearer token, API key, or other service credential
2. the caller sends it in `@auth_` using a `union.Auth_` variant
3. `onAuth` validates the credential and returns normalized internal headers
4. middleware and handlers authorize from the normalized identity

If an intermediary gateway or transport already owns the raw credential, it can
still translate that transport-specific credential into `@auth_` before the
Telepact server processes the request.

## Recommended path in one sentence

Model caller credentials in `union.Auth_`, move them through `@auth_`, normalize
them with `onAuth`, authorize on normalized identity, and keep transport- and
deployment-specific auth mechanics outside Telepact itself.
