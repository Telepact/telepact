# Core Concepts

This page gives the shortest high-level map of Telepact's main ideas before you
dive into the detailed guides.

## Message shape

Telepact messages are always two JSON objects in an array:

```json
[headers, body]
```

- the first object holds headers
- the second object holds one request or response payload

Requests usually look like:

```json
[{}, {"fn.example": {"field": 1}}]
```

Responses usually look like:

```json
[{}, {"Ok_": {"field": 1}}]
```

For a more complete walkthrough, start with the
[Quickstart](../example.md) or [Learn Telepact by Example](../01-learn-by-example/README.md).

## Schema role

The Telepact schema is the contract that drives the whole ecosystem.

It defines:

- function arguments and results
- reusable structs and unions
- shared errors and headers
- what counts as valid requests and responses

That one schema also powers:

- server-side validation
- documentation rendering
- client code generation
- mock servers
- compatibility checks

For the full language, see the [Schema Writing Guide](./01-schema-guide.md).

## Headers versus body

The body contains the main request or response payload.

Headers are separate metadata that travel alongside that payload. They are where
Telepact puts cross-cutting concerns such as auth, request ids, binary
negotiation, and select directives.

As a rule of thumb:

- use the body for domain data and function arguments/results
- use headers for metadata and transport-adjacent control signals

For more detail, see:

- [Transport Guide](../03-build-clients-and-servers/01-transports.md)
- [Operating Boundary Guide](../04-operate/01-production-guide.md)
- [FAQ](../05-background-and-reference/01-faq.md)

## Function links

Telepact functions can appear as data types inside other payloads. That lets a
server return a pre-populated function call that a client can follow later.

This gives Telepact a hypermedia-like capability without requiring HTTP-specific
link formats.

See:

- [Learn by Example: Functions](../01-learn-by-example/02-schema/08-functions.md)
- [Demos](../../example/README.md)

## Select

Telepact supports response shaping through the `@select_` header. Clients can
ask for fewer fields from a response graph without inventing a separate query
language.

See:

- [Learn by Example: Select](../01-learn-by-example/03-opt-in-features/12-select.md)
- [Extensions](./03-extensions.md)

## Binary

Telepact can negotiate a compact binary representation at runtime. This means a
client can keep a JSON-first development workflow and still upgrade to binary
when it wants more efficiency.

See:

- [Learn by Example: Binary](../01-learn-by-example/03-opt-in-features/13-binary.md)
- [Learn by Example: Automatic binary negotiation](../01-learn-by-example/06-using-telepact-client-library-code/20-automatic-binary-negotiation.md)

## Where to go next

- If you are designing an API, go to the [Schema Writing Guide](./01-schema-guide.md).
- If you are building a client, go to [Client Paths](../03-build-clients-and-servers/02-client-paths.md).
- If you are building a server, go to [Server Paths](../03-build-clients-and-servers/03-server-paths.md).
- If you want the CLI and related workflows, go to [Tooling Workflow](../03-build-clients-and-servers/04-tooling-workflow.md).
