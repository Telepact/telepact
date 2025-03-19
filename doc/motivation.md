
# Motivation

| Capability                                        | OpenAPI | gRPC | GraphQL | MsgPact |
| ------------------------------------------------- | ------- | ---- | ------- | ---- |
| No transport restrictions                         | ❌      | ❌   | ❌      | ✅   |
| No transport details leaked into API              | ❌      | ✅   | ✅      | ✅   |
| No string parsing/splicing                        | ❌      | ✅   | ✅      | ✅   |
| Low development burden for servers                | ✅      | ✅   | ❌      | ✅   |
| No required libraries for clients                 | ✅      | ❌   | ❌      | ✅   |
| Type-safe generated code                          | 🤔      | ✅   | ✅      | ✅   |
| Human-readable wire-format                        | ✅      | ❌   | 🤔      | ✅   |
| Built-in binary data serialization protocol       | ❌      | ✅   | ❌      | ✅   |
| Built-in dynamic response shaping                 | ❌      | ❌   | ✅      | ✅   |
| No required ABI                                   | ✅      | ❌   | ✅      | ✅   |
| Expressive distinction between null and undefined | ❌      | ❌   | ❌      | ✅   |
| Built-in API documentation distribution           | ❌      | ❌   | ❌      | ✅   |
| Built-in mocking for tests                        | ❌      | ❌   | ❌      | ✅   |

## Why not RESTful APIs?

RESTful APIs are familiar to many developers and are highly accessible due to
reliance on ubiquitous tooling like HTTP and JSON. However, RESTful APIs by
definition rely on HTTP and cannot be used across other IPC boundaries, limiting
their use. RESTful APIs also tend to leak transport details into the API
definition itself, which often leads to design inefficiencies where API design
is stalled to answer HTTP-specific questions, such as determining the right url
structure, query parameters, HTTP method, HTTP status code, etc. Type-safe code
generation for RESTful APIs is in development with OAS and is generally
available with limitations.

## Why not gRPC?

gRPC APIs are highly efficient and leverage critical improvements offered by the
HTTP/2 specification. They are also type-safe through generated code boundaries
derived from a wholistic IDL that does not leak transport details. However, gRPC
lacks overall accessibility due to reliance on heavy toolchains with generated
code in a finite number of programming languages. And there are some API design
limitations with gRPC, such as prohibitive rules with lists (i.e. repeated
values), a lack of distinction between null and undefined, and a weak error
model at the protocol layer which has prompted patching at the library level
with limited coverage across the gRPC ecosystem.

## Why not GraphQL?

GraphQL is a unique API technology that features a custom query language to
dynamically build data payloads from a pre-crafted set of server-side functions.
While consumption of the "graph" is extremely expressive for clients,
construction of the graph's backing functions places a modest burden on
server-side development to properly and efficiently integrate the query engine
with the backing database. GraphQL also has limited accessibility as clients
largely rely on GraphQL libraries to construct the query strings so as to
minimize parse error risk. GraphQL does feature a rich data model, but it lacks
support for common programming idioms, such as dictionaries. While binary
serialization is technically possible through manual configuration, it is
largely not observed in practice due to the accessibility tax it would incur on
both servers and clients.

## Why MsgPact?

MsgPact takes all of the strengths of REST, gRPC, and GraphQL and combines them
into a simple but careful design. It is built, first and foremost, on JSON with
transport agnosticism to maximize accessibility to clients that want to
integrate using only the native JSON and networking capabilities of their
preferred programming language and/or industry standard library. It achieves
type safety through built-in server-side validation against a server-defined API
schema, complete with typing options that allow for modeling all common
programming data types. And then from that baseline, MsgPact critically allows
clients to upgrade their experience as deemed appropriate by the client,
optionally using:

-   MsgPact client libraries that help facilitate crafting of MsgPact messages
-   Generated code for further increased type safety
-   A built-in binary serialization protocol for optimized efficiency
-   A built-in mechanism to omit fields from responses for optimized efficiency

These client features are built-in via the MsgPact library used by the server, such
that all of these features are available to the client automatically, without
any configuration by the server.
