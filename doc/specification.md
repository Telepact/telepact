# Telepact Specification

## 1. Status and scope

This document is a language-runtime-agnostic, RFC-style specification for the
core Telepact model.

It specifies:

- the Telepact message envelope
- the schema language and definition kinds
- the standard request/response contract
- the reserved headers and built-in ecosystem behaviors
- the transport boundary and compatibility model

It does not specify:

- a particular programming language API
- a particular transport such as HTTP or WebSocket
- deployment topology or implementation internals

## 2. Conformance language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
this document are to be interpreted as described in RFC 2119.

## 3. Core terms

- A **message** is the wire-level request or response envelope.
- A **schema** is the Telepact contract that defines valid messages.
- A **function** is a request/response entrypoint named `fn.*`.
- A **struct** is a JSON object shape named `struct.*`.
- A **union** is a tagged sum type named `union.*`.
- A **header** is metadata carried in the first object of a message.
- A **result union** is the response body union for a function.

## 4. Transport model

Telepact is transport-agnostic.

- A transport is responsible only for moving request bytes to a server and
  returning response bytes to a client.
- Telepact semantics are defined above the transport.
- A conforming Telepact server MUST accept request bytes, decode them as a
  Telepact message, validate them against the active schema, execute the target
  function, validate the response, and return response bytes.
- A conforming Telepact client MAY use plain JSON tooling, a Telepact runtime
  library, generated code, or any other transport-capable implementation that
  emits valid Telepact messages.

No particular transport metadata system is required because Telepact headers are
carried inside the message envelope itself.

## 5. Message envelope

### 5.1 General shape

A Telepact message MUST be a JSON array of exactly two objects:

```json
[headers, body]
```

- `headers` MUST be a JSON object.
- `body` MUST be a JSON object containing exactly one entry.

If a message cannot be parsed into this shape, it is invalid.

### 5.2 Request messages

A request body MUST contain exactly one function call:

```json
[{}, {"fn.hello": {"name": "Ada"}}]
```

- the body key MUST name a function defined as `fn.*`
- the body value MUST validate against that function's argument struct

### 5.3 Response messages

A response body MUST contain exactly one result tag:

```json
[{}, {"Ok_": {"message": "Hello Ada"}}]
```

- the body key MUST be one tag from the target function's result union
- the body value MUST validate against that tag's payload struct

Every function result union MUST contain `Ok_`. Any non-`Ok_` tag is treated as
an error outcome by convention and by Telepact tooling.

## 6. Headers

Headers occupy the first object in the message.

- Declared header names MUST begin with `@`.
- Declared header names MUST match `^@[a-z][a-zA-Z0-9_]*$`.
- Header fields are always optional.
- Header definitions MUST NOT use the `!` suffix.
- Additional undeclared headers MUST be allowed at runtime.

Headers are intended for metadata and control signals such as authentication,
correlation ids, timeouts, selection, and binary negotiation. Domain data
SHOULD remain in the body.

## 7. Schema source model

### 7.1 Schema directories

When a Telepact implementation loads a schema directory:

- it MUST read only the immediate files in that directory
- it MUST accept `*.telepact.yaml` and `*.telepact.json`
- it MAY mix YAML and JSON files in one directory
- it MUST reject subdirectories as schema inputs
- it MUST treat the directory as the unordered union of all supported files

File order MUST NOT affect schema meaning.

### 7.2 YAML and JSON forms

Checked-in YAML is an authoring format. The canonical lowered schema model is
JSON-shaped. YAML and JSON schema files therefore describe the same logical
definitions.

## 8. Type system

### 8.1 Scalar types

The built-in scalar type expressions are:

- `"boolean"`
- `"integer"`
- `"number"`
- `"string"`
- `"any"`
- `"bytes"`

`"any"` accepts any JSON value except `null`.

`"bytes"` denotes binary data. In JSON form, bytes are represented as strings
because JSON has no native bytes type.

### 8.2 Collections

Telepact collection types are:

- `[T]` for arrays of `T`
- `{"string": T}` for objects with string keys and values of `T`

### 8.3 Nullability

A scalar type expression MAY be suffixed with `?` to permit `null`:

- `"string?"`
- `"integer?"`
- `"any?"`

Nullability applies to type strings. Arrays and objects are not directly
nullable in the Telepact type syntax.

### 8.4 Optional fields

A struct field name MAY be suffixed with `!` to indicate that the field may be
omitted from instances:

```yaml
- struct.User:
    id: "string"
    nickname!: "string"
```

The `!` suffix is part of the field name on live payloads. For example,
`"nickname!"` remains the payload key.

## 9. Definition kinds

A schema is an array of top-level definitions. The core definition kinds are
`info.*`, `struct.*`, `union.*`, `fn.*`, `errors.*`, and `headers.*`.

### 9.1 Info definitions

An `info.*` definition is schema metadata.

- it identifies or describes the schema at a high level
- it does not participate as a normal data type
- implementations MAY surface it prominently in documentation and schema browsing

### 9.2 Struct definitions

A `struct.*` definition declares a JSON object shape.

- all fields are required unless marked optional with `!`
- additional fields are not allowed
- a struct name MAY be referenced as a type expression

### 9.3 Union definitions

A `union.*` definition declares a tagged sum type.

- a union MUST contain at least one tag
- each tag payload is a struct
- a union instance MUST contain exactly one tag
- a union name MAY be referenced as a type expression

### 9.4 Function definitions

A `fn.*` definition declares one request/response operation.

- the request side is an argument struct
- the response side is a result union written under `->:`
- the result union MUST include `Ok_`

Example:

```yaml
- fn.divide:
    x: "number"
    y: "number"
  ->:
    - Ok_:
        result: "number"
    - ErrorCannotDivideByZero: {}
```

Functions MAY be used as type expressions in non-top-level payloads. In that
form, a function value is a pre-populated call object:

```json
{"fn.divide": {"x": 6, "y": 3}}
```

This enables Telepact's hypermedia-like link behavior.

### 9.5 Errors definitions

An `errors.*` definition declares reusable error tags that are automatically
appended to the result union of all user-defined functions.

- `errors.*` definitions MUST NOT be used as ordinary type expressions
- they are intended for systemic cross-cutting errors, not for domain data that
  is better modeled directly in function results

### 9.6 Headers definitions

A `headers.*` definition declares request and response header shapes:

```yaml
- headers.Id_:
    "@id_": "any"
  ->:
    "@id_": "any"
```

- request headers are declared before `->:`
- response headers are declared under `->:`
- all declared header fields are optional
- undeclared header fields remain valid at runtime

### 9.7 Docstrings

Top-level definitions and union tags MAY include docstrings via `///:`. These
docstrings are part of the schema authoring model and power documentation
rendering.

## 10. Standard definitions

Telepact automatically extends user schemas with built-in definitions.

### 10.1 Always-present definitions

The standard internal schema includes at least:

- `fn.ping_`
- `fn.api_`
- standard validation and parse errors
- internal header definitions such as `@unsafe_`, `@select_`, `@bin_`, and `@id_`

`fn.api_` returns the user-facing schema by default. When requested with
`includeInternal!`, it also returns Telepact internal definitions. When
requested with `includeExamples!`, it also returns deterministic example
payloads.

### 10.2 Conditional auth definitions

If a schema defines `union.Auth_`, Telepact MUST also expose:

- the `@auth_` header typed as `union.Auth_`
- `ErrorUnauthenticated_`
- `ErrorUnauthorized_`

### 10.3 Mock definitions

Telepact mock servers MAY expose additional mock-control definitions such as
stub creation and verification, plus reserved extension types used only for mock
workflows.

## 11. Reserved headers and behaviors

This section summarizes the core reserved behaviors exposed through built-in
headers.

### 11.1 `@id_`

`@id_` is a correlation header. A conforming server SHOULD reflect the
client-provided value unchanged in the response.

### 11.2 `@time_`

`@time_` communicates a client timeout budget in integer form.

### 11.3 `@unsafe_`

If `@unsafe_` is `true`, a server MAY disable response validation for that
request. When honored, the response SHOULD reflect the provided `@unsafe_`
value.

### 11.4 `@select_`

`@select_` carries an `_ext.Select_` value that narrows the response graph.

- selection applies to response data, not to request argument shapes
- selection may target the active result union via `->`
- selection may target reachable `struct.*` and `union.*` types

### 11.5 `@bin_`, `@enc_`, and `@pac_`

Telepact binary support is negotiated at runtime rather than through a required
code-generation ABI.

- a client MAY send `@bin_` with one or more known encoding checksums
- a server MUST return its supported checksum in `@bin_`
- if the client checksum does not match, the server SHOULD also return `@enc_`,
  the active field-name to field-id map
- a response MAY be encoded in binary
- `@pac_` indicates use of packed binary encoding strategy

## 12. Validation and failure model

### 12.1 Request validation

A server MUST validate:

- request headers against the effective header schema
- request body against the called function argument schema

Invalid requests MUST produce schema-level error results rather than entering the
user function logic.

### 12.2 Response validation

A server MUST validate the response headers and body it is about to send, unless
response validation has been explicitly disabled for that request by supported
runtime behavior such as `@unsafe_`.

### 12.3 Standard failure outcomes

The standard internal schema defines canonical failures for:

- parse failure
- invalid request headers
- invalid request body
- invalid response headers
- invalid response body
- unknown server failure

These failures are part of the wire contract, independent of local runtime
exception shapes.

## 13. Compatibility model

Telepact is designed for schema-first evolution.

Schema changes SHOULD be evaluated for backwards compatibility before release.
Compatible evolution patterns include:

- adding optional struct fields
- adding new functions
- adding new union tags when consumers can safely ignore unknown possibilities

Incompatible changes generally include:

- changing an existing field type
- removing required fields
- removing existing functions or result shapes still relied on by clients

Telepact tooling is expected to compare an older schema to a newer one and
report backwards-incompatible changes.

## 14. Design intent

Telepact combines several goals:

- plain JSON participation for minimal clients
- optional richer tooling through libraries and code generation
- transport independence
- runtime binary negotiation
- response shaping without a separate query language
- schema-driven documentation, mocking, and compatibility checks

These properties are consequences of the schema and message model defined above.

## 15. Related documents

- [Core Concepts](./core-concepts.md)
- [Schema Writing Guide](./schema-guide.md)
- [Extensions](./extensions.md)
- [Transport Guide](./transports.md)
- [Production Guide](./production-guide.md)
- [FAQ](./faq.md)
