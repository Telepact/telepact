# Introduction

jAPI (pronounced "Jay-Pee-Eye") or **J**SON **A**pplication **P**rogramming
**I**nterface is an API expressed purely with JSON. Familiar API concepts, such
as function calls and return values, are represented entirely with JSON
payloads. Consequently, A jAPI can satisfy API needs across not only HTTP, but
any inter-process communication boundary.

Wherever JSON can go, a jAPI can be served 🚀

HTTP client example (with `cURL`):

```bash
$ export URL=http://example.com/api/v1
$ curl -X '["function.add", {"Authorization": "Bearer <token>"}, {"x": 1, "y": 2}]' $URL
["function.add", {}, {"result": 3}]
$ curl -X '["function.sub", {"Authorization": "Bearer <token>"}, {"x": 1, "y": 2}]' $URL
["function.sub", {}, {"result": -1}]
```

Websocket client example (with `python`):

```python
# japi_ws.py

import sys
import json
from websocket import create_connection
ws = create_connection('ws://example.com/api/v1')
ws.send(sys.argv[1])
print('{}'.format((ws.recv())))
```

```
$ python japi_ws.py '["function.add", {"Authorization": "Bearer <token>"}, {"x": 1, "y": 2}]'
["function.add", {}, {"result": 3}]
$ python japi_ws.py '["function.sub", {"Authorization": "Bearer <token>"}, {"x": 1, "y": 2}]'
["function.add", {}, {"result": -1}]
```

# Motivation

| Capability                                                 | RESTful | gRPC | GraphQL | jAPI |
| ---------------------------------------------------------- | ------- | ---- | ------- | ---- |
| Transport agnosticism (can use something other than HTTP)  | ❌      | ❌   | ✅      | ✅   |
| API design cleanly separated from transport                | ❌      | ✅   | ✅      | ✅   |
| Maximally expressive API design options                    | ✅      | ❌   | ❌      | ✅   |
| Low development burden for servers                         | ✅      | ✅   | ❌      | ✅   |
| No required libraries for clients                          | ✅      | ❌   | ❌      | ✅   |
| Type-safe generated code                                   | 🤔      | ✅   | ✅      | ✅   |
| Developer-friendly data serialization protocol with JSON   | ✅      | ❌   | ✅      | ✅   |
| Compact and efficient data serialization protocol          | ❌      | ✅   | ❌      | ✅   |
| Built-in client-driven selection of serialization protocol | ❌      | ❌   | ❌      | ✅   |
| Built-in client-driven dynamic response shaping            | ❌      | ❌   | ✅      | ✅   |

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

gRPC APIs are highly efficient and leverages critical improvements offered by
the HTTP/2 specification. They are also type-safe through generated code
boundaries derived from a wholistic IDL that does not leak transport details.
However, gRPC lacks overall accessibility due to reliance on libraries in a
finite number of programming languages and expectation to generate code. And
there are some API design limitations with gRPC, such as prohibitive rules with
lists (i.e. repeated values), a lack of distinction between null and undefined,
and a weak error model at the protocol layer which has prompted patching at the
library level with limited coverage across the gRPC ecosystem.

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

## Why jAPI?

jAPI takes all of the strengths of REST, gRPC, and GraphQL and combines them
into a simple but careful design. It is built, first and foremost, on JSON with
transport agnosticism to maximize accessibility to clients that want to
integrate using only the native JSON and networking capabilities of their
preferred programming language and/or industry standard library. It achieves
type safety through built-in server-side validation against a server-defined API
schema, complete with typing options that allow for modeling all common
programming data types. And then from that baseline, jAPI critically allows
clients to upgrade their experience as deemed appropriate by the client,
optionally using:

- jAPI client libraries that help facilitate crafting of jAPI messages
- Generated code for further increased type safety
- A built-in binary serialization protocol for optimized efficiency
- A built-in mechanism to omit fields from responses for optimized efficiency

These client features are built-in via the jAPI library used by the server, such
that all of these features are available to the client automatically, without
any configuration by the server.

## More FAQ

### Why have both optional and nullable fields?

jAPI allows API designers to mark a field as optional (the field might be
omitted) as well as mark the field type as nullable (the field might appear with
a null value).

These design options are both present to maximize the design expressiveness of
the API. jAPI leverages optionality to accomplish the expressiveness of
`undefined` in languages like TypeScript. While `null` is a value that can be
passed around like a string or number, `undefined` or optionality can not be
passed around but is rather an incidental property of the shape of the data
itself. This is especially useful in update APIs where you want to erase just
one field of a model, where null can be used to indicate the erasure of data,
and optionality can be used to omit all fields except the one field you want to
erase.

### Why do functions in jAPI not support positional arguments?

jAPI functions are automatically associated with an argument struct and an
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

### Why are enums in jAPI not like traditional enums seen in C or Java?

jAPI enums take the form of the tagged unions paradigm as featured in modern
programming languages like rust. In the particular case of jAPI, it is very
similar to the traditional enum, except that a struct is automatically attached
to each enum value.

This design maximizes backwards compatible change points in the API design, as
adding an optional field to a struct is a legal backwards compatible change. The
traditional enum can be approximated by simply leaving all enum structs blank.

### Why force servers to perform result validation?

jAPI automatically performs validation of function results (as well as errors)
against the jAPI schema, and there is no setting for servers to turn off this
behavior.

This design decision is intentional. It helps maintain the high standard of type
safety in the jAPI ecosystem by preventing API providers from indulging in the
plausible deniability of claiming malformed data is just an inconvenience and
are instead forced to deal with a hard failure through bug reports. Hard
failures also help draw attention to type safety deficits early in the
development phase.

Clients who are uniquely vulnerable to hard server failures and who find it
advantageous to receive the malformed data anyway and adapt on-the-fly are able
to turn off this result validation by submitting their requests with the
`{"_unsafe":true}` header.

### If all I want is compact binary serialization, why not just use gRPC?

jAPI and gRPC both have compact binary serialization for drastically improved
efficiency over conventional serialization such as JSON. However, jAPI brings a
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

jAPI breaks free from the conventional practice of defining and maintaining
field ids, and instead accomplishes client and server agreement over field ids
through a client-server handshake at runtime. In consequence, jAPI boasts a far
simpler developer experience during the API design phase as well as the unique
privilege of allowing clients to leverage binary serialization without generated
code.

### Why can't I have a other non-error result enum values?

The only required value for the function result enum is `ok`. All other values
in the result enum that are not `ok` are, by definition, "not okay", and will be
interpreted as an error in all circumstances. API designers are encouraged to
prefix additional result enum values with `error` or equivalent to improve
readability and recognition of errors.

### Is adding a new enum value a backwards compatible change?

Many API technologies will classify adding a new enum value to an existing enum
as a backwards incompatible change. This is due to the potential risk of a
client driving critical code paths off an enum value, and the emergence of a new
enum value begets undefined behavior in that critical path, which invites bugs.
And some technologies may suffer build-time failures due to the fact that many
API technologies integrate directly with programming languages through generated
code incorporating native enums, and many of these languages will simply not
compile when a new enum value appears in the context of a `switch` or `match`
statement until that new value has a handling procedure implemented.

jAPI takes the stance that adding a new enum value to an existing enum _is_ a
backwards compatible change, on the basis of the following:

- Enums are powerful typing constructs that replace otherwise type unsafe
  patterns, and classifying evolution of an enum as backwards incompatible
  discourages use, violating jAPI's core principles of encouraging the strongest
  of type patterns.
- jAPI does not run the risk of build-time failures with enums since jAPI enums
  are represented as special objects rather than native enums.
- Clients are capable of implementing error-prone code regardless of how a
  server evolves it's API, and jAPI cannot uphold its core principle of enabling
  API evolution if it holds servers accountable for client-side design failures.
  Clients can neglect proper handling of null, derive internal non-public
  implementation details by parsing strings, or base critical computation on an
  assumption that a boolean is always true. And a server would be able to break
  such clients by suddenly returning null, changing the string to a different
  pattern, or returning false, but this breakage would not be due to "backwards
  incompatible" changes. The client made invalid assumptions, which may further
  yet be a consequence of choosing a riskier type unsafe technology stack that
  failed to highlight such invalid assumptions. And in the same way that a
  client should not make assumptions about patterns in strings or neglect `else`
  cases on its critical paths, a client should not make assumptions about
  patterns in enums or neglect enum default branch logic.

## Glossary

- **Body** - A structured JSON object containing the primary data payload of the
  jAPI Message.

- **Client** - An entity consuming a jAPI.

- **Argument** - The colloquial name for the body of a `function.*`-targeted
  jAPI Message sent from the Client.

- **Headers** - An unstructured JSON object consisting of metadata about a jAPI
  Message.

- **Message** - The JSON payload sent over the IPC boundary, comprised of a
  single JSON array with 3 elements: (1) the target, (2) headers, (3) body.

- **Result** - The colloquial name for the body of a `function.*`-targeted jAPI
  Message sent from the Server.

- **Server** - An entity providing an implementation of a jAPI and adhering to
  the jAPI specification.

- **Target** - A reference to a top-level definition in the jAPI description of
  the jAPI server.

- **jAPI Schema** - The JSON document describing the API. This document is
  written in the JSON language following a jAPI-flavored JSON schema, but
  conventionally, this document would be written using an IDL.

# Navigation

- [Specification](SPECIFICATION.md)
