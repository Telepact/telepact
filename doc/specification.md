# Telepact Specification

This document is a language-agnostic, RFC-like description of Telepact's core
contract.

Telepact is a transport-agnostic API ecosystem built around one idea: the
message on the wire stays close to ordinary JSON, while a shared schema defines
what those messages mean. Everything else in the ecosystem—validation,
documentation, code generation, mocking, response shaping, and binary
negotiation—builds on that contract.

This specification is organized around three themes:

1. the message envelope, including unstructured headers and the structured body
2. the schema that defines valid requests and responses
3. the reserved extension mechanism used for context-sensitive behavior

## 1. Message envelope

### 1.1 Logical shape

A Telepact message is logically a two-element array:

```json
[headers, body]
```

- `headers` MUST be a JSON object
- `body` MUST be a JSON object

In JSON form, that array is serialized directly. In binary form, the same
logical message is preserved, but the bytes may use a negotiated field-id
encoding.

### 1.2 Headers: unstructured metadata

The first element of the message is the headers object.

Headers carry metadata and control information that travel alongside the main
payload. They are intentionally looser than the body:

- all headers are optional
- undeclared headers are still allowed
- schema authors may document and type-check specific headers, but validation
  does not reject additional header keys

Headers are where Telepact places cross-cutting concerns such as:

- authentication and request context
- correlation ids
- response shaping
- timeout hints
- binary negotiation
- warnings

Defined header names use the `@name` form. Common built-in examples include
`@id_`, `@time_`, `@unsafe_`, `@select_`, `@bin_`, `@enc_`, `@pac_`, and
`@warn_`.

Headers are intentionally less rigid than ordinary data structures. They are
meant to support transport-adjacent concerns without forcing those concerns into
the request or response payload itself.

### 1.3 Body: structured payload

The second element of the message is the body object.

Unlike headers, the body is fully structured by the schema:

- a request body names exactly one function target
- a response body names exactly one result tag
- the selected target determines the payload shape
- unknown or misplaced body keys are invalid

Typical request:

```json
[{}, {"fn.add": {"x": 1, "y": 2}}]
```

Typical response:

```json
[{}, {"Ok_": {"result": 3}}]
```

For requests:

- the top-level body key MUST be a `fn.*` name
- the payload MUST validate against that function's argument struct

For responses:

- the top-level body key MUST be one tag from the function's result union
- the payload MUST validate against that tag's struct
- `Ok_` is the required success tag for every function result
- other result tags are treated as non-success outcomes and are typically used
  for explicit errors

### 1.4 Naming and reserved internal forms

Telepact distinguishes public API definitions from internal ecosystem
definitions by naming convention:

- internal names end with `_`
- user-defined names normally do not end with `_`

Examples of internal names include `fn.ping_`, `fn.api_`, `ErrorUnknown_`, and
the built-in `_ext.*_` extension types.

### 1.5 Functions as data

A function definition can also appear as a type expression inside another
payload. In that position, the function behaves like a link-shaped value: it is
an object with one `fn.*` key and a pre-populated argument payload.

This allows Telepact APIs to return callable next steps as data without
requiring a transport-specific link format.

## 2. Schema

### 2.1 Role of the schema

The schema is the contract that defines what counts as a valid Telepact
interaction.

One schema drives:

- request validation
- response validation
- documentation rendering
- client code generation
- mock-server behavior
- compatibility analysis

The schema therefore defines not only static types, but the shared meaning of
the whole Telepact interface.

### 2.2 Files and schema directories

Telepact schemas are authored as:

- `*.telepact.yaml`
- `*.telepact.json`

When a runtime or tool loads a schema directory, it treats the immediate schema
files in that directory as one unordered schema. Subdirectories are not part of
the schema.

YAML is the preferred checked-in format because it is easier to read and works
well with multi-line docstrings. JSON remains the canonical lowered form and the
closest representation of the wire-aligned structure.

### 2.3 Definition kinds

A Telepact schema is an array of top-level definitions. The primary definition
kinds are:

- `struct.*` for product types
- `union.*` for tagged sum types
- `fn.*` for request/response operations
- `errors.*` for shared systemic errors
- `headers.*` for request/response header contracts

These definitions are deliberately few. Telepact prefers a small set of stable,
composable shapes over a larger catalog of special-purpose constructs.

### 2.4 Type system

Telepact type expressions are JSON-shaped. Core scalar types are:

- `"boolean"`
- `"integer"`
- `"number"`
- `"string"`
- `"any"`

Collection forms are:

- arrays, written as `["type"]`
- string-keyed maps, written as `{"string": "type"}`

Named references may point to `struct.*`, `union.*`, or `fn.*` definitions where
allowed.

Nullability is expressed by appending `?` to a scalar or named type string, for
example `"string?"`.

Optional object fields are expressed by appending `!` to the field name. That
same `!` remains in live request and response payloads, keeping wire data close
to the schema and making optionality visible to readers.

### 2.5 Structs, unions, and functions

`struct.*` defines an object with fixed field names and typed values. Unknown
fields are not allowed.

`union.*` defines a tagged object where exactly one tag is present, and that tag
maps to a struct payload. Empty payload structs are allowed.

`fn.*` combines:

- an argument struct
- a result union introduced by `->`

Every function result MUST contain an `Ok_` tag. Additional tags may define
explicit error results or other non-success outcomes.

Functions are the entrypoints of the Telepact API surface. A request chooses a
function; a response chooses one tag from that function's result union.

### 2.6 Shared errors and shared headers

`errors.*` definitions inject systemic error tags into every user-defined
function result. They are intended for cross-cutting runtime failures such as
invalid requests, invalid responses, parse failures, or other server-wide error
conditions.

`headers.*` definitions describe the request and response headers associated with
interactions. They resemble structs, but with different rules:

- header names use the `@name` form
- all defined headers are implicitly optional
- header names MUST NOT use the `!` suffix
- additional undeclared headers remain valid

This asymmetry is intentional: bodies are strict application data, while headers
are a flexible metadata channel.

### 2.7 Standard definitions

Telepact runtimes automatically add standard internal definitions to the schema.
These include:

- utility functions such as `fn.ping_` and `fn.api_`
- built-in headers used for selection, binary negotiation, ids, timing, and
  warnings
- standard validation and parse errors

As a result, every Telepact server exposes more than just the user-authored API.
It also exposes the standard ecosystem contract that makes tools and runtimes
interoperate predictably.

## 3. Extensions

### 3.1 Purpose

Telepact reserves `_ext.*_` names for built-in extension types.

An extension exists when a normal declarative schema entry is not expressive
enough because the valid payload depends on surrounding schema context. In other
words, extension validation is context-sensitive rather than purely local.

That is why extension definitions appear in internal schema as placeholders such
as:

```yaml
- _ext.Select_: {}
```

The empty object is not the full definition. It signals that Telepact runtimes
provide special validation, example generation, and semantics for that reserved
name.

### 3.2 Extension model

Extensions follow these rules:

- the `_ext.*_` namespace is reserved
- extension semantics are defined by Telepact itself, not by service authors
- extension payloads still use ordinary JSON values
- the valid shape may depend on the active function or reachable schema graph

Extensions are therefore part of the Telepact protocol contract, even though
their rules are not written as ordinary `struct.*` or `union.*` declarations.

### 3.3 Standard extensions

Current standard extensions include:

- `_ext.Select_`, used by the `@select_` header to narrow response fields
- `_ext.Call_`, used by mock verification to represent one observed function call
- `_ext.Stub_`, used by mock control to represent one stubbed call/result pair

`_ext.Select_` is driven by the active function result and the reachable
structs/unions beneath it. `_ext.Call_` and `_ext.Stub_` are driven by the
functions present in the mocked schema.

### 3.4 Discovery and use

Extensions are internal, but they are discoverable. Calling `fn.api_` with
`includeInternal!` returns the internal schema entries, including `_ext.*_`
placeholders. Calling it with `includeExamples!` adds deterministic examples.

Service authors SHOULD treat extensions as reserved protocol features, not as a
general authoring pattern for custom data modeling. Ordinary API data SHOULD
continue to use `struct.*`, `union.*`, `fn.*`, `errors.*`, and `headers.*`.

## Scope boundaries

This specification describes Telepact's message contract, schema contract, and
extension mechanism. It does not require any specific transport, programming
language runtime, code generator, or deployment topology.

HTTP, WebSockets, NATS, stdio, queues, and other transports may all carry
Telepact messages as long as they preserve the message semantics defined here.

## See also

- [Core Concepts](./core-concepts.md)
- [Schema Writing Guide](./schema-guide.md)
- [Extensions](./extensions.md)
- [Transport Guide](./transports.md)
- [FAQ](./faq.md)
