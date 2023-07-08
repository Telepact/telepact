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
| No required libraries for clients                          | ✅      | ❌   | ✅      | ✅   |
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
lists (i.e. repeated values) as well as a weak error model at the protocol layer
which has limited patching at the library level across the gRPC ecosystem.

## Why not GraphQL?

GraphQL is a highly accessible API technology that features a unique query
language to dynamically build data payloads as needed from a pre-crafted set of
server-side functions. However, GraphQL tends to create its pristine client
development experience at the expense of server-side development, as an
understanding of the query model is required to properly design the functions
that plug into that query engine. And in some cases, lifting complex data joins
out of a database and into server memory may be prohibitively slow for some
large data sets. It does features a rich data model, but it lacks support for
common programming idioms, such as variable maps. While binary serialization is
technically possible through manual configuration, it is largely not observed in
practice due to the accessibility tax it would incur on both servers and
clients.

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

- jAPI client libraries that help facilitate crafting of JSON payloads
- Generated code for further increased type safety
- A built-in binary serialization protocol for optimized efficiency
- A built-in mechanism to omit fields from responses for further optimized
  efficiency

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

### Why are enums in jAPI not like traditional enums seen in C or Java?

jAPI enums take the form of the tagged unions paradigm as featured in modern
programming languages like rust. In the particular case of jAPI, it is very
similar to the traditional enum, except that a struct is automatically attached
to each enum value.

This design maximizes backwards compatible change points in the API design, as
adding a field to a struct is a legal backwards compatible change. The
traditional enum can be approximated by simply leaving all structs blank.

### Why force servers to perform output validation? Wouldn't it be better to give clients malformed data so that they are at least empowered to adapt?

jAPI automatically performs validation of function outputs (as well as errors)
against the API description, and there is no setting for servers to turn off
this behavior.

This design decision is intentional. It helps maintain the high standard of type
safety in the jAPI ecosystem by preventing API providers from indulging in the
plausible deniability of claiming malformed data is just an inconvenience and
are instead forced to deal with a hard failure through bug reports. Hard
failures also help draw attention to type safety deficits early in the
development phase.

Clients who are uniquely vulnerable to hard server failures and who find it
advantageous to receive the malformed data anyway and adapt on-the-fly are able
to turn off this output validation by submitting their requests with the
`{"_unsafe":true}` header.

## Glossary

- **Body** - A structured JSON object containing the primary data payload of the
  jAPI Message.

- **Client** - An entity consuming a jAPI.

- **Input** - The body of a `function.*`-targeted jAPI Message sent from the
  Client.

- **Headers** - An unstructured JSON object consisting of metadata about a jAPI
  Message.

- **Message** - The JSON payload sent over the IPC boundary, comprised of a
  single JSON array with 3 elements: (1) the target, (2) headers, (3) body.

- **Output** - The body of a `function.*`-targeted jAPI Message sent from the
  Server.

- **Server** - An entity providing an implementation of a jAPI and adhering to
  the jAPI specification.

- **Target** - A reference to a top-level definition in the jAPI description of
  the jAPI server.

- **jAPI Schema** - The JSON document describing the API. This document is
  written in the JSON language following a particular JSON schema, but
  conventionally, this document would be written using an IDL.

# Navigation

- [Specification](SPECIFICATION.md)
