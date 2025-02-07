# Introduction

uAPI is an API expressed purely with JSON. Familiar API concepts, such
as function calls and return values, are represented entirely with JSON
payloads. Consequently, A uAPI can satisfy API needs across not only HTTP, but
any inter-process communication boundary.

Wherever JSON can go, a uAPI can be served 🚀

No required client-side toolchains. Many client-side experiences. One
server-side experience.

HTTP client example (with `cURL`):

```bash
$ export URL=http://example.com/api/v1
$ curl -X '[{"Authorization": "Bearer <token>"}, {"fn.add": {"x": 1, "y": 2}}]' $URL
[{}, {"Ok_": {"result": 3}}]
$ curl -X '[{"Authorization": "Bearer <token>"}, {"fn.sub": {"x": 1, "y": 2}}]' $URL
[{}, {"Ok_": {"result": -1}}]
```

Websocket client example (with `python`):

```python
# uapi_ws.py

import sys
import json
from websocket import create_connection
ws = create_connection('ws://example.com/api/v1')
ws.send(sys.argv[1])
print('{}'.format((ws.recv())))
```

```
$ python uapi_ws.py '[{"Authorization": "Bearer <token>"}, {"fn.add": {"x": 1, "y": 2}}]'
[{}, {"Ok_": {"result": 3}}]
$ python uapi_ws.py '[{"Authorization": "Bearer <token>"}, {"fn.sub": {"x": 1, "y": 2}}]'
[{}, {"Ok_": {"result": -1}}]
```

# Motivation

| Capability                                                | OpenAPI | gRPC | GraphQL | uAPI |
| --------------------------------------------------------- | ------- | ---- | ------- | ---- |
| Transport agnosticism (can use something other than HTTP) | ❌      | ❌   | ✅      | ✅   |
| No transport details leaked into API                      | ❌      | ✅   | ✅      | ✅   |
| No string parsing/splicity                                | ❌      | ✅   | ✅      | ✅   |
| Support for dictionary data structures                    | ✅      | ❌   | ❌      | ✅   |
| Low development burden for servers                        | ✅      | ✅   | ❌      | ✅   |
| No required libraries for clients                         | ✅      | ❌   | ❌      | ✅   |
| Type-safe generated code                                  | 🤔      | ✅   | ✅      | ✅   |
| Human-readable wire-format                                | ✅      | ❌   | 🤔      | ✅   |
| Compact and efficient data serialization protocol         | ❌      | ✅   | ❌      | ✅   |
| Built-in dynamic response shaping                         | ❌      | ❌   | ✅      | ✅   |
| No ABI                                                    | ✅      | ❌   | ✅      | ✅   |
| Expressive distinction between null and undefined         | ❌      | ❌   | ❌      | ✅   |
| Built-in API documentation distribution                   | ❌      | ❌   | ❌      | ✅   |
| Built-in mocking for tests                                | ❌      | ❌   | ❌      | ✅   |

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
lacks overall accessibility due to reliance on libraries in a finite number of
programming languages and expectation to generate code. And there are some API
design limitations with gRPC, such as prohibitive rules with lists (i.e.
repeated values), a lack of distinction between null and undefined, and a weak
error model at the protocol layer which has prompted patching at the library
level with limited coverage across the gRPC ecosystem.

## Why not GraphQL?

GraphQL is a unique API technology that features a custom query language to
dynamically build data payloads from a pre-crafted set of server-side functions.
While consumption of the "graph" is extremely expressive for clients,
construction of the graph's backing functions places a modest burden on
server-side development to properly and efficiently integrate the query engine
with the backing database. GraphQL also has limited accessibility as clients
largely rely on GraphQL libraries to construct the query strings so as to
minimize parse error risk. GraphQL does feature a rich data model, but it lacks
support for common programming idioms, such as variable maps. While binary
serialization is technically possible through manual configuration, it is
largely not observed in practice due to the accessibility tax it would incur on
both servers and clients.

## Why uAPI?

uAPI takes all of the strengths of REST, gRPC, and GraphQL and combines them
into a simple but careful design. It is built, first and foremost, on JSON with
transport agnosticism to maximize accessibility to clients that want to
integrate using only the native JSON and networking capabilities of their
preferred programming language and/or industry standard library. It achieves
type safety through built-in server-side validation against a server-defined API
schema, complete with typing options that allow for modeling all common
programming data types. And then from that baseline, uAPI critically allows
clients to upgrade their experience as deemed appropriate by the client,
optionally using:

-   uAPI client libraries that help facilitate crafting of uAPI messages
-   Generated code for further increased type safety
-   A built-in binary serialization protocol for optimized efficiency
-   A built-in mechanism to omit fields from responses for optimized efficiency

These client features are built-in via the uAPI library used by the server, such
that all of these features are available to the client automatically, without
any configuration by the server.

## More FAQ

### Why have both optional and nullable fields?

uAPI allows API designers to mark a field as optional (the field might be
omitted) as well as mark the field type as nullable (the field might appear with
a null value).

These design options are both present to maximize the design expressiveness of
the API. uAPI leverages optionality to accomplish the expressiveness of
`undefined` in languages like TypeScript. While `null` is a value that can be
passed around like a string or number, `undefined` or optionality can not be
passed around but is rather an incidental property of the shape of the data
itself. This is especially useful in update APIs where, for example, if you want
to erase just one field of a model, where null can be used to indicate the
erasure of data, and optionality can be used to omit all fields except the one
field you want to erase.

### Why do functions in uAPI not support positional arguments?

uAPI functions are automatically associated with an argument struct and an
result struct that API designers can use to colloquially define arguments and
return values, respectively. The colloquial arguments being supplied via the
argument struct will be inherently unordered due to the nature of JSON objects,
and there is no way to approximate traditional positional arguments at the root
of the Request Message Body.

This design decision is intentional. Positional arguments are a significant risk
that provoke backwards incompatible changes through seemingly innocent API
changes, such as changing the order of arguments or appending new arguments.
This problem is especially pronounced in generated code for many programming
languages. By making the design entry point a struct, API designers are
predisposed for backwards-compatible changes like appending optional struct
fields.

### Why is there no Enum type like seen in C or Java?

uAPI achieves enumerated types with unions, which are very similar to enums as
seen in C or Java, except that a struct is automatically attached to each value.
The traditional enum can be approximated by simply leaving all union structs
blank.

### Why force servers to perform response validation?

uAPI automatically performs validation of responses against the uAPI schema, and
there is no setting for servers to turn off this behavior.

This design decision is intentional. It helps maintain the high standard of type
safety in the uAPI ecosystem by denying API providers the option to respond
to malformed data as an inconvenience and are instead forced to deal with hard
failures through bug reports. Hard failures also help draw attention to type
safety deficits early in the development phase.

Clients who are uniquely vulnerable to hard server failures and who find it
advantageous to receive the malformed data anyway and adapt on-the-fly are able
to turn off this response validation by submitting their requests with the
`{"unsafe_":true}` header.

### If all I want is compact binary serialization, why not just use gRPC?

uAPI and gRPC both have compact binary serialization for drastically improved
efficiency over conventional serialization such as JSON. However, uAPI brings a
critical new innovation to the space of RPC and binary serialization in that it
_does not leak the ABI into the API_.

ABI, or Application _Binary_ Interface, is the actual interface between RPC
clients and servers using such compact serialization protocols. The data passing
through this interface is unreadable due to conventional json keys being encoded
as numbers. Because an encoding is in play, clients and servers need to agree on
what numbers represent which fields all throughout the API. gRPC and other
conventional RPC frameworks accomplish this by having the clients and servers
both base their field ids on the same information during code generation by
leaking these ABI field ids into the API schema itself. Unfortunately, this adds
an unusual cognitive burden for developers designing such APIs, because they now
need to guard against interface drift between the API and the ABI, typically by
complying with a set of policies concerning how those field ids are defined and
how they can change.

uAPI breaks free from the conventional practice of defining and maintaining
field ids, and instead accomplishes client and server agreement over field ids
through a client-server handshake at runtime. In consequence, uAPI boasts a far
simpler developer experience during the API design phase as well as the unique
privilege of allowing clients to leverage binary serialization without generated
code.

### Why can't I have other non-error result union values?

The only required tag for the function result union is `Ok_`. All other tags
in the result union that are not `Ok_` are, by definition, "not okay", and will
be interpreted as an error in all circumstances. API designers are encouraged to
prefix additional result union tags with `Error` or equivalent to improve
readability and recognition of errors.

### Why can't I associate a union tag to something besides a struct?

A designer might want to treat a union tag like a struct field, and associate
any data type with a tag. However, in uAPI, all tags in unions are associated
with a struct, which means you can't associate union tags with simpler data
types, like booleans or strings.

This restriction is in place to uphold uAPI's value of prioritizing effective
software evolution. Unions, like functions, are entrypoints to unique
execution paths in software, so if software evolves such that an execution
path requires a new "argument" like a integer, that requirement will percolate
up to the entrypoint. If the proverbial API designer chose to associate the
union tag directly a boolean, the API would require a breaking change to make
room for this new integer "argument." In contrast, uAPI establishing the
expectation that all union tags are associated with structs means the backwards
compatible option of adding a new struct field is always available to
software designers dealing with the needs of evolving software.

### Why can I not omit fn.\* fields using the `"select_"` header?

The `"select_"` header is used to omit fields from structs, which includes
union structs, but not the argument struct included with function definitions.

The function type exists so that API providers may incorporate "links" into
their API design, such that the appearance of a function type payload can
simply be copied and pasted verbatim into the body a new message. Tooling like
the uAPI console specifically utilizes this technique to allow end-users to
"click through" graphs designed by the API provider.

Omitting fields in the argument struct disrupts the API provider's ability
to established well-defined links, and consequently, the `"select_"` header is
disallowed from omitting fields in function argument structs.
