---
name: telepact-api
description: Reference and implementation guidance for Telepact schemas, libraries, and SDKs.
metadata:
  short-description: Telepact API reference
---

# Introduction

Telepact is an API ecosystem for bridging programs across inter-process
communication boundaries.

What makes Telepact different? It takes the differentiating features of the
industry's most popular API technologies, and combines them together through 3
key innovations:

1. **JSON as a Query Language** - API calls and `SELECT`-style queries are all
   achieved with JSON abstractions, giving first-class status to clients
   wielding only a JSON library
2. **Binary without code generation** - Binary protocols are established through
   runtime handshakes, rather than build-time code generation, offering binary
   efficiency to clients that want to avoid code generation toolchains
3. **Hypermedia without HTTP** - API calls can return functions with pre-filled
   arguments, approximating a link that can be followed, all achieved with pure
   JSON abstractions

For further reading, see [Motivation](#motivation).

For explanations of various design decisions, see [the FAQ](#faq).

For how-to guides, see the [API Schema Guide](#schema-writing-guide), as well as
the library and SDK docs:

-   [Library: Typescript](#telepact-library-for-typescript)
-   [Library: Python](#telepact-library-for-python)
-   [Library: Java](#telepact-library-for-java)

-   [SDK: CLI](#telepact-cli)
-   [SDK: Developer Console](#telepact-console)
-   [SDK: Prettier Plugin](#telepact-prettier-plugin)

# At a glance

Specify your API:

```sh
$ cat ./api/math.telepact.json
```

```json
[
    {
        "///": " Divide two integers, `x` and `y`. ",
        "fn.divide": {
            "x": "integer",
            "y": "integer"
        },
        "->": [
            {
                "Ok_": {
                    "result": "number"
                }
            },
            {
                "ErrorCannotDivideByZero": {}
            }
        ]
    }
]
```

Serve it with one of the Telepact libraries over a transport of your choice:

```sh
$ cat ./server.py
```

```py
from telepact import TelepactSchemaFiles, TelepactSchema, Server, Message
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

async def handler(req_msg):
    fn = req_msg.get_body_target()
    args = req_msg.body[fn]
    if fn == 'fn.divide':
        x = args['x']
        y = args['y']
        if y == 0:
            return Message({}, {'ErrorCannotDivideByZero': {}})

        result = x / y
        return Message({}, {'Ok_': {'result': result}})
    else:
        raise Exception('Unknown function')

options = Server.Options()
options.auth_required = False

schema_files = TelepactSchemaFiles('./api')
api = TelepactSchema.from_file_json_map(schema_files.filenames_to_json)
server = Server(api, handler, options)

async def http_handler(request):
    request_bytes = await request.body()
    response = await server.process(request_bytes)
    response_bytes = response.bytes
    media_type = 'application/octet-stream' if 'bin_' in response.headers else 'application/json'
    return Response(content=response_bytes, media_type=media_type)

routes = [
    Route('/api/telepact', endpoint=http_handler, methods=['POST']),
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
]

app = Starlette(routes=routes, middleware=middleware)

uvicorn.run(app, host='0.0.0.0', port=8000)
```

```sh
$ poetry add uvicorn starlette telepact
$ poetry run python ./server.py
```

Then tell your clients about your transport, and they can consume your API with
minimal tooling:

```
$ cat ./client.js
```

```js
let header = {};
let body = {
    "fn.divide": {
        x: 6,
        y: 3,
    }
};
let request = [header, body];
let response = await fetch(
    "http://localhost:8000/api/telepact",
    {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
    },
);
console.log(`Response: ${JSON.stringify(await response.json())}`);
```

```sh
$ node ./client.js
Response: [{},{"Ok_":{"result":2}}]
```

Or clients can also leverage telepact tooling to:

-   Select less fields to reduce response sizes
-   Generate code to increase type safety
-   Use binary serialization to reduce request/response sizes

# Licensing

Telepact is licensed under the Apache License, Version 2.0. See
[LICENSE](LICENSE) for the full license text. See [NOTICE](NOTICE) for
additional information regarding copyright ownership.


---

# Motivation

## Principles

1. **Accessibility** - Whether you're bringing sophisticated toolchains or a
   minimialist setup, you can easily participate in Telepact with the
   complexity-level you need, from plain json to generated code with efficient
   binary serialization.
2. **Portability** - Telepact definitions take the form of currency in the
   Telepact ecosystem, unlocking powerful "based on" features such as
   documentation rendering, code completion, mocking, and code generation.
3. **Trust** - Features are governed not by server implementations, but rather
   by the Telepact ecosystem itself; consequently, clients can confidently
   integrate with all Telepact servers with robust expectations.
4. **Stability** - Telepact's interface description language offers a powerful
   but carefully curated list of paradigms to ensure API designs don't fall
   victim to common API evolution pitfalls.

## Summary

| Capability                                        | OpenAPI | gRPC | GraphQL | Telepact |
| ------------------------------------------------- | ------- | ---- | ------- | -------- |
| No transport restrictions                         | ❌      | ❌   | ❌      | ✅       |
| No transport details leaked into API              | ❌      | ✅   | ✅      | ✅       |
| No string parsing/splicing                        | ❌      | ✅   | ✅      | ✅       |
| Low development burden for servers                | ✅      | ✅   | ❌      | ✅       |
| No required libraries for clients                 | ✅      | ❌   | ❌      | ✅       |
| Type-safe generated code                          | 🤔      | ✅   | ✅      | ✅       |
| Human-editable wire-format                        | ✅      | ❌   | 🤔      | ✅       |
| Built-in binary data serialization protocol       | ❌      | ✅   | ❌      | ✅       |
| Built-in dynamic response shaping                 | ❌      | ❌   | ✅      | ✅       |
| No required ABI                                   | ✅      | ❌   | ✅      | ✅       |
| Expressive distinction between null and undefined | ❌      | ❌   | ❌      | ✅       |
| Built-in API documentation distribution           | 🤔      | ❌   | ✅      | ✅       |
| Built-in mocking for tests                        | ❌      | ❌   | ❌      | ✅       |

## Why not RESTful APIs?

RESTful APIs are familiar to many developers and are highly accessible due to
reliance on ubiquitous tooling like HTTP and JSON. However, RESTful APIs rely on
HTTP and cannot be used across other IPC boundaries, limiting their use. RESTful
APIs also tend to leak transport details into the API definition itself, which
often leads to design inefficiencies where API design is stalled to answer
HTTP-specific questions, such as determining the right url structure, query
parameters, HTTP method, HTTP status code, etc. Type-safe code generation for
RESTful APIs is in development with OAS and is generally available with
limitations.

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

## Why Telepact?

Telepact takes all of the strengths of REST, gRPC, and GraphQL and combines them
into a simple but careful design. It is built, first and foremost, on JSON with
transport agnosticism to maximize accessibility to clients that want to
integrate using only the native JSON and networking capabilities of their
preferred programming language and/or industry standard library. It achieves
type safety through built-in server-side validation against a server-defined API
schema, complete with typing options that allow for modeling all common
programming data types. And then from that baseline, Telepact critically allows
clients to upgrade their experience as deemed appropriate by the client,
optionally using:

-   Telepact client libraries that help facilitate crafting of Telepact messages
-   Generated code for further increased type safety
-   A built-in binary serialization protocol for optimized efficiency
-   A built-in mechanism to omit fields from responses for optimized efficiency

These client features are built-in via the Telepact library used by the server,
such that all of these features are available to the client automatically,
without any configuration by the server.


---

# FAQ

## Why have both optional and nullable fields?

Telepact allows API designers to mark a field as optional (the field might be
omitted) as well as mark the field type as nullable (the field might appear with
a null value).

These design options are both present to maximize the design expressiveness of
the API. Telepact leverages optionality to accomplish the expressiveness of
`undefined` in languages like TypeScript. While `null` is a value that can be
passed around like a string or number, `undefined` or optionality can not be
passed around but is rather an incidental property of the shape of the data
itself. This is especially useful in update APIs where, for example, if you want
to erase just one field of a model, where null can be used to indicate the
erasure of data, and optionality can be used to omit all fields except the one
field you want to erase.

## Why can I not define nullable arrays or objects?

Nullability is indicated on base types by appending type strings with `?`, but
since collection types are defined with native JSON array and object syntax,
using `[]` and `{}` respectively, there is no way to append `?` to these
expressions since free `?` characters are not legal JSON syntax.

This apparent design constraint, albeit coincidental, aligns with Telepact's
design goals of expressibility without redundant design options. In Telepact,
null represents "empty" (while optional represents "unknown"). Since array and
object collection types can already express "emptiness," nullability is
unnecessary.

## Why is there nothing like a standard 404 Not Found error?

Telepact provides several standard errors to represent common integration
issues, such as request and response incompatibilities and
authentication/authorization errors, all reminisicent of the 400, 500, 401 and
403 error codes, respectively, but there is no standard error that approximates
404 Not Found.

Instead, API designers are encouraged to abstract concepts as data whenever
possible, and the 404 Not Found use-case can be trivially represented with an
empty optional value.

## But the given 400-like Bad Request errors are too precise. Why is a more general-purpose "Bad Request" error not available?

Telepact has several errors to communicate request invalidity with respect to
the API schema, but there is no out-of-the-box "Bad Request" error that a server
can raise from some custom validation logic in the server handler.

Overly generalized abstractions, such as a catch-all "Bad Request", are
unpreferred in Telepact in favor of precise data types. Where necessary, all
"Bad Request" use-cases can be enumerated in function results alongside the
`Ok_` tag. API designers are encouraged to prefer data abstractions over errors
wherever possible, such as preferring empty optionals over "Not Found" errors.

## Why do functions in Telepact not support positional arguments?

Telepact functions are automatically associated with an argument struct and a
result struct that API designers can use to define arguments and return values,
respectively. The arguments being supplied via the argument struct will be
inherently unordered due to the nature of JSON objects, and there is no way to
approximate traditional positional arguments at the root of the Request Message
Body.

This design decision is intentional. Positional arguments are a significant risk
that provoke backwards incompatible changes through seemingly innocent API
changes, such as changing the order of arguments or appending new arguments.
This problem is especially pronounced in generated code for many programming
languages. By making the design entry point a struct, API designers are
predisposed for backwards-compatible changes like appending optional struct
fields.

## Why is there no Enum type as seen in C or Java?

Telepact achieves enumerated types with unions, which are very similar to enums
as seen in C or Java, except that a struct is automatically attached to each
value. The traditional enum can be approximated by simply leaving all union
structs blank.

## Why force servers to perform response validation?

Telepact automatically performs validation of responses against the Telepact
schema, and there is no setting for servers to turn off this behavior.

This design decision is intentional. It helps maintain the high standard of type
safety in the Telepact ecosystem by denying API providers the option of
categorizing malformed data as an inconvenience and are instead forced to deal
with hard failures through bug reports. Hard failures also help draw attention
to type safety deficits early in the development phase.

Clients who are uniquely vulnerable to hard server failures and who find it
advantageous to receive the malformed data anyway are able to turn off this
response validation by submitting their requests with the `{"@unsafe_":true}`
header.

## If all I want is compact binary serialization, why not just use gRPC?

Telepact and gRPC both have compact binary serialization for drastically
improved efficiency over conventional serialization such as JSON. However,
Telepact brings a critical new innovation to the space of RPC and binary
serialization in that it _does not leak the ABI into the API_.

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

Telepact breaks free from the conventional practice of defining and maintaining
field ids, and instead accomplishes client and server agreement over field ids
through a client-server handshake at runtime. In consequence, Telepact boasts a
far simpler developer experience during the API design phase as well as the
unique privilege of allowing clients to leverage binary serialization without
generated code.

## Why can't I have other non-error result union values?

The only required tag for the function result union is `Ok_`. All other tags in
the result union that are not `Ok_` are, by definition, "not okay", and will be
interpreted as an error in all circumstances. API designers are encouraged to
prefix additional result union tags with `Error` or equivalent to improve
readability and recognition of errors.

## Why can't I associate a union tag to something besides a struct?

A designer might want to treat a union tag like a struct field, and associate
any data type with a tag. However, in Telepact, all tags in unions are
associated with a struct, which means you can't associate union tags with
simpler data types, like booleans or strings.

This restriction is in place to uphold Telepact's value of prioritizing
effective software evolution. Unions, like functions, are entrypoints to unique
execution paths in software, so if software evolves such that an execution path
requires a new "argument" like a integer, that requirement will percolate up to
the entrypoint. If the proverbial API designer chose to associate the union tag
directly to a boolean, the API would require a breaking change in the form of
creating another tag to make room for this new integer "argument" to sit next to
the original boolean. In contrast, Telepact establishing the expectation that
all union tags are associated with structs means the backwards compatible option
of adding a new struct field is always available to software designers dealing
with the needs of evolving software.

## Why can I not omit fn.\* fields using the `"@select_"` header?

The `"@select_"` header is used to omit fields from structs, which includes
union structs, but not the argument struct included with function definitions.

The function type exists so that API providers may incorporate "links" into
their API design, such that the appearance of a function type payload can simply
be copied and pasted verbatim into the body a new message. Tooling like the
Telepact console specifically utilizes this technique to allow end-users to
"click through" graphs designed by the API provider.

Omitting fields in the argument struct disrupts the API provider's ability to
established well-defined links, and consequently, the `"@select_"` header is
disallowed from omitting fields in function argument structs.


---

# Schema Writing Guide

This guide will explain how to understand and write `*.telepact.json` files.

## Type Expression

Types are expressed with a string, which may be contained within conventional
JSON collection types. When using JSON objects in type expressions, the only
allowed key type is `"string"`.

| Type Expression           | Example allowed JSON values           | Example disallowed JSON values                  |
| ------------------------- | ------------------------------------- | ----------------------------------------------- |
| `"boolean"`               | `true`, `false`                       | `null`, `0`                                     |
| `"integer"`               | `1`, `0`, `-1`                        | `null`, `0.1`                                   |
| `"number"`                | `0.1`, `-0.1`                         | `null`, `"0"`                                   |
| `"string"`                | `""`, `"text"`                        | `null`, `0`                                     |
| `["boolean"]`             | `[]`, `[true, false]`                 | `null`, `0`, `[null]` `{}`                      |
| `{"string": "integer"}`   | `{}`, `{"k1": 0, "k2": 1}`            | `null`, `0`, `{"k": null}`, `[]`                |
| `[{"string": "boolean"}]` | `[{}]`, `[{"k1": true, "k2": false}]` | `[{"k1": null}]`, `[{"k1": 0}]`, `[null]` `[0]` |
| `"any"`                   | `false`, `0`, `0.1`, `""`, `[]`, `{}` | `null`                                          |

### Nullability

The `?` symbol can be appended to type strings to indicate nullability. Note
that it is not possible to express nullable arrays or objects.

| Type Expression            | Example allowed JSON values                   | Example disallowed JSON values |
| -------------------------- | --------------------------------------------- | ------------------------------ |
| `"boolean?"`               | `null`, `true`, `false`                       | `0`                            |
| `"integer?"`               | `null`, `1`, `0`, `-1`                        | `0.1`                          |
| `"number?"`                | `null`, `0.1`, `-0.1`                         | `"0"`                          |
| `"string?"`                | `null`, `""`, `"text"`                        | `0`                            |
| `["boolean?"]`             | `[]`, `[true, false, null]`                   | `null`, `0`, `{}`              |
| `{"string": "integer?"}`   | `{}`, `{"k1": 0, "k2": 1, "k3": null}`        | `null`, `0`, `[]`              |
| `[{"string": "boolean?"}]` | `[{}]`, `[{"k1": null, "k2": false}]`         | `[{"k1": 0}]`, `[null]` `[0]`  |
| `"any?"`                   | `null`, `false`, `0`, `0.1`, `""`, `[]`, `{}` | (none)                         |

## Definitions

A Telepact Schema is an array of the following definition patterns:

-   struct
-   union
-   function
-   errors
-   headers

### Struct Definition

Type expressions can be encased in a structured object (product type). Struct
definitions may be used in any type expression.

The `!` symbol can be appended to a field name to indicate that it is optional.

```json
[
    {
        "struct.ExampleStruct1": {
            "field": "boolean",
            "anotherField": ["string"]
        }
    },
    {
        "struct.ExampleStruct2": {
            "optionalField!": "boolean",
            "anotherOptionalField!": "integer"
        }
    }
]
```

| Type Expression             | Example allowed JSON values                           | Example disallowed JSON values     |
| --------------------------- | ----------------------------------------------------- | ---------------------------------- |
| `"struct.ExampleStruct1"`   | `{"field": true, "anotherField": ["text1", "text2"]}` | `null`, `{}`                       |
| `"struct.ExampleStruct2"`   | `{"optionalField!": true}`, `{}`                      | `null`, `{"wrongField": true}`     |
| `["struct.ExampleStruct2"]` | `[{"optionalField!": true}]`                          | `[null]`, `[{"wrongField": true}]` |

### Union

Type expressions can be encased in a tagged structured object (sum type). Unions
may be used in any type expression.

At least one tag is required.

```json
[
    {
        "union.ExampleUnion1": [
            {
                "Tag": {
                    "field": "integer"
                }
            },
            {
                "EmptyTag": {}
            }
        ]
    },
    {
        "union.ExampleUnion2": [
            {
                "Tag": {
                    "optionalField!": "string"
                }
            }
        ]
    }
]
```

| Type Expression         | Example allowed JSON values                          | Example disallowed JSON values                |
| ----------------------- | ---------------------------------------------------- | --------------------------------------------- |
| `"union.ExampleUnion1"` | `{"Tag": {"field": 0}}`, `{"EmptyTag": {}}`          | `null`, `{}`, `{"Tag": {"wrongField": true}}` |
| `"union.ExampleUnion2"` | `{"Tag": {"optionalField!": "text"}}`, `{"Tag": {}}` | `null`, `{}`                                  |

### Function

Request-Response semantics can be defined with functions. A function is a
combination of an argument struct and a result union. The result union requires
at least the `Ok_` tag. By convention, all non-`Ok_` tags are considered errors.

Clients interact with servers through functions. The client submits JSON data
valid against the function argument struct definition, and the server responds
with JSON data valid against the function result union.

When referenced as a type in type expressions, the result union is unused.
Functions cannot be used in type expressions that extend down from a top-level
function argument.

```json
[
    {
        "fn.exampleFunction1": {
            "field": "integer",
            "optionalField!": "string"
        },
        "->": [
            {
                "Ok_": {
                    "field": "boolean"
                }
            }
        ]
    },
    {
        "fn.exampleFunction2": {},
        "->": [
            {
                "Ok_": {}
            },
            {
                "Error": {
                    "field": "string"
                }
            }
        ]
    }
]
```

| Example Request                               | Example Response                     |
| --------------------------------------------- | ------------------------------------ |
| `[{}, {"fn.exampleFunction1": {"field": 1}}]` | `[{}, {"Ok_": {"field": true}}]`     |
| `[{}, {"fn.exampleFunction2": {}}]`           | `[{}, {"Error": {"field": "text"}}]` |

| Type Expression         | Example allowed JSON values                              | Example disallowed JSON values |
| ----------------------- | -------------------------------------------------------- | ------------------------------ |
| `"fn.exampleFunction1"` | `{"field": 0}`, `{"field": 1, "optionalField!": "text"}` | `null`, `{}`                   |
| `"fn.exampleFunction2"` | `{}`                                                     | `null`, `{"wrongField": 0}`    |

### Errors

Errors definitions are similar to unions, except that the tags are automatically
added to the result union of all user-defined functions. Errors definitions
cannot be used in type expressions.

API designers should be careful to avoid using errors definitions to abstract
"reusable" errors. Errors definitions are only intended for systemic server
errors that could be encountered by any function.

```json
[
    {
        "errors.ExampleErrors1": [
            {
                "Error1": {
                    "field": "integer"
                }
            },
            {
                "Error2": {}
            }
        ]
    }
]
```

For example, if placed in the same schema, the above error definition would
apply the errors `Error1` and `Error2` to both the `fn.exampleFunction1` and
`fn.exampleFunction2` functions from the previous section, as indicated below
(Note, the following example only illustrates the effect of the errors
definition at schema load time; the original schema is not re-written.)

```json
[
    {
        "fn.exampleFunction1": {
            "field": "integer",
            "optionalField!": "string"
        },
        "->": [
            {
                "Ok_": {
                    "field": "boolean"
                }
            },
            {
                "Error1": {
                    "field": "integer"
                }
            },
            {
                "Error2": {}
            }
        ]
    },
    {
        "fn.exampleFunction2": {},
        "->": [
            {
                "Ok_": {}
            },
            {
                "Error": {
                    "field": "string"
                }
            },
            {
                "Error1": {
                    "field": "integer"
                }
            },
            {
                "Error2": {}
            }
        ]
    }
]
```

### Headers

Headers definitions are similar to function definitions in that they correlate
to the request/response semantics, but only with respect to the headers object
on the Telepact message. Both the request and response definitions resemble
struct definitions, with a few exceptions:

-   all header fields must be prepended with `@`
-   all header fields are implicitly optional
-   additional header fields not specified in the definition will be allowed
    during validation

Headers definitions cannot be used in type expressions.

```json
[
    {
        "headers.Example": {
            "@requestHeader": "boolean",
            "@anotherRequestHeader": "integer"
        },
        "->": {
            "@responseHeader": "string"
        }
    }
]
```

| Example Request                                       | Example Response                              |
| ----------------------------------------------------- | --------------------------------------------- |
| `[{"@requestHeader": true}, {"fn.ping_": {}}]`        | `[{"@responseHeader": "text"}, {"Ok_": {}}]`  |
| `[{"@anotherRequestHeader": true}, {"fn.ping_": {}}]` | `[{"@unspecifiedHeader": true}, {"Ok_": {}}]` |

| Example Invalid Request                     | Example Invalid Response                |
| ------------------------------------------- | --------------------------------------- |
| `[{"@requestHeader": 1}, {"fn.ping_": {}}]` | `[{"@responseHeader": 1}, {"Ok_": {}}]` |

### Docstrings

All top-level definitions and union tags (including errors and function results)
can include a docstring. Docstrings support markdown when rendered in the
Telepact console.

#### Single-line

```json
[
    {
        "///": " A struct that contains a `field`. ",
        "struct.ExampleStruct": {
            "field": "boolean"
        }
    },
    {
        "struct.ExampleUnion": [
            {
                "///": " The default `Tag` that contains a `field`. ",
                "Tag": {
                    "field": "integer"
                }
            }
        ]
    }
]
```

#### Multi-line

Multi-line docstrings are supported. For readability and ease of writing, schema
writers are encouraged to use the Telepact Prettier plugin. (The Telepact
console uses the prettier plugin in draft mode.)

```json
[
    {
        "///": [
            " A struct that contains a field.                     ",
            "                                                     ",
            " Fields:                                             ",
            "  - `field` (type: `boolean`)                        "
        ],
        "struct.ExampleStruct": {
            "field": "boolean"
        }
    }
]
```

## Automatic Definitions

Some definitions are automatically appended to your schema at runtime.

### Standard Definitions

Standard definitions include utility functions, like `fn.ping_`, and common
errors, like `ErrorInvalidRequest` and `ErrorUnknown_`. These are always
included and cannot be turned off.

You can find all standard definitions
[here](#internal-telepact-json).

### Auth Definitions

Auth definitions include the `@auth_` header and the `ErrorUnauthenticated_` and
`ErrorUnauthorized_` errors. These are included conditionally if the API writer
defines a `struct.Auth_` definition in their schema, for the auth header
definition data type references it, as in `"@auth_": "struct.Auth_"`.

API writiers are strongly encouraged to place all auth-related data into the
standard `struct.Auth_` struct, as the `@auth_` header is treated with greater
sensitivity throughout the Telepact ecosystem.

You can find details about auth definitions
[here](#auth-telepact-json).

### Mock Definitions

Mock definitions include mocking functions, like `fn.createStub_` and
`fn.verify_` for use in tests. These definitions are included if the API is
served with a `MockServer` rather than a `Server` in the Telepact server-side
library.

You can find all mock defnitions
[here](#mock-internal-telepact-json).

## Full Example

### Schema

```json
[
    {
        "///": " A calculator app that provides basic math computation capabilities. ",
        "info.Calculator": {}
    },
    {
        "///": " A function that adds two numbers. ",
        "fn.add": {
            "x": "number",
            "y": "number"
        },
        "->": [
            {
                "Ok_": {
                    "result": "number"
                }
            }
        ]
    },
    {
        "///": " A value for computation that can take either a constant or variable form. ",
        "union.Value": [
            {
                "Constant": {
                    "value": "number"
                }
            },
            {
                "Variable": {
                    "name": "string"
                }
            }
        ]
    },
    {
        "///": " A basic mathematical operation. ",
        "union.Operation": [
            {
                "Add": {}
            },
            {
                "Sub": {}
            },
            {
                "Mul": {}
            },
            {
                "Div": {}
            }
        ]
    },
    {
        "///": " A mathematical variable represented by a `name` that holds a certain `value`. ",
        "struct.Variable": {
            "name": "string",
            "value": "number"
        }
    },
    {
        "///": " Save a set of variables as a dynamic map of variable names to their value. ",
        "fn.saveVariables": {
            "variables": { "string": "number" }
        },
        "->": [
            {
                "Ok_": {}
            }
        ]
    },
    {
        "///": " Compute the `result` of the given `x` and `y` values. ",
        "fn.compute": {
            "x": "union.Value",
            "y": "union.Value",
            "op": "union.Operation"
        },
        "->": [
            {
                "Ok_": {
                    "result": "number"
                }
            },
            {
                "ErrorCannotDivideByZero": {}
            }
        ]
    },
    {
        "///": " Export all saved variables, up to an optional `limit`. ",
        "fn.exportVariables": {
            "limit!": "integer"
        },
        "->": [
            {
                "Ok_": {
                    "variables": ["struct.Variable"]
                }
            }
        ]
    },
    {
        "///": " A function template. ",
        "fn.getPaperTape": {},
        "->": [
            {
                "Ok_": {
                    "tape": ["struct.Computation"]
                }
            }
        ]
    },
    {
        "///": " A computation. ",
        "struct.Computation": {
            "user": "string?",
            "firstOperand": "union.Value",
            "secondOperand": "union.Value",
            "operation": "union.Operation",
            "result": "number?",
            "successful": "boolean"
        }
    },
    {
        "fn.showExample": {},
        "->": [
            {
                "Ok_": {
                    "link": "fn.compute"
                }
            }
        ]
    },
    {
        "errors.RateLimit": [
            {
                "ErrorTooManyRequests": {}
            }
        ]
    },
    {
        "headers.Identity": {
            "@user": "string"
        },
        "->": {}
    }
]
```

### Valid Client/Server Interactions

```
-> [{}, {"fn.ping_": {}}]
<- [{}, {"Ok_": {}}]

-> [{}, {"fn.add": {"x": 1, "z": 2}}]
<- [{}, {"ErrorInvalidRequestBody_": {"cases": [{"path": ["fn.add", "z"], "reason": {"ObjectKeyDisallowed": {}}}, {"path": ["fn.add"], "reason": {"RequiredObjectKeyMissing": {"key": "y"}}}]}}]

-> [{}, {"fn.add": {"x": 1, "y": 2}}]
<- [{}, {"Ok_": {"result": 3}}]

-> [{}, {"fn.saveVariables": {"a": 1, "b": 2}}]
<- [{}, {"Ok_": {}}]

-> [{}, {"fn.showExample": {}}]
<- [{}, {"Ok_": {"link": {"fn.compute": {"x": {"Constant": {"value": 5}}, "y": {"Variable": {"name": "b"}}, "op": {"Mul": {}}}}}}]

-> [{"@user": "bob"}, {"fn.compute": {"x": {"Constant": {"value": 5}}, "y": {"Variable": {"name": "b"}}, "op": {"Mul": {}}}}]
<- [{}, {"Ok_": {"result": 10}}]

-> [{"@user": "bob"}, {"fn.compute": {"x": {"Variable": {"name": "a"}}, "y": {"Constant": {"value": 0}}, "op": {"Div": {}}}}]
<- [{}, {"ErrorCannotDivideByZero": {}}]

-> [{}, {"fn.getPaperTape": {}}]
<- [{}, {"Ok_": {"tape": [{"user": null, "firstOperand": {"Constant": {"value": 1}}, "secondOperand": {"Constant": {"value": 2}}, "operation": {"Add": {}}, "result": 3, "successful": true}, {"user": "bob", "firstOperand": {"Constant": {"value": 5}}, "secondOperand": {"Variable": {"name": "b"}}, "operation": {"Mul": {}}, "result": 10, "successful": true}, {"user": "bob", "firstOperand": {"Variable": {"name": "a"}}, "secondOperand": {"Constant": {"value": 0}}, "operation": {"Div": {}}, "result": null, "successful": false}]}}]

-> [{}, {"fn.exportVariables": {}}]
<- [{}, {"Ok_": {"variables": [{"name": "a", "value": 1}, {"name": "b", "value": 2}]}}]

-> [{}, {"fn.exportVariables": {"limit!": 1}}]
<- [{}, {"Ok_": {"variables": [{"name": "a", "value": 1}]}}]

-> [{}, {"fn.add": {"x": 1, "y": 2}}]
<- [{}, {"ErrorTooManyRequests": {}}]

-> [{}, {"fn.showExample": {}}]
<- [{}, {"ErrorTooManyRequests": {}}]
```


---

# Telepact Library for TypeScript

## Installation

```
npm install telepact
```

## Usage

API:
```json
[
    {
        "fn.greet": {
            "subject": "string"
        },
        "->": {
            "Ok_": {
                "message": "string"
            }
        }
    }
]
```

Server:
```ts
import * as fs from 'fs';
import * as path from 'path';

const files = new TelepactSchemaFiles('/directory/containing/api/files', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);

const handler = async (requestMessage: Message): Promise<Message> => {
    const functionName = Object.keys(requestMessage.body)[0];
    const arguments = requestMessage.body[functionName];

    try {
        // Early in the handler, perform any pre-flight "middleware" operations, such as
        // authentication, tracing, or logging.
        log.info("Function started", {function: functionName});

        // Dispatch request to appropriate function handling code.
        // (This example uses manual dispatching, but you can also use a more advanced pattern.)
        if (functionName == 'fn.greet') {
            var subject = arguments['subject'];
            return new Message({}, {Ok_: {message: `Hello ${subject}!`}});
        }

        throw new Error('Function not found');
    } finally {
        // At the end the handler, perform any post-flight "middleware" operations
        log.info("Function finished", {function: functionName});
    }
};

const options = new ServerOptions();
const server = new Server(schema, handler, options);

// Wire up request/response bytes from your transport of choice
transport.receive(async (requestBytes): Promise<Message> => {
    const response = await server.process(requestBytes);
    return response.bytes;
});
```

Client:
```ts
const adapter: (m: Message, s: Serializer) => Promise<Message> = async (m, s) => {
    const requestBytes = s.serialize(m);

    // Wire up request/response bytes to your transport of choice
    const responseBytes = await transport.send(requestBytes);

    return s.deserialize(responseBytes);
};

const options = new ClientOptions();
const client = new Client(adapter, options);

// Inside an async function in your application:
const request = new Message({}, { 'fn.greet': { subject: 'World' } });
const response = await client.request(request);
if (response.getBodyTarget() === 'Ok_') {
    const okPayload = response.getBodyPayload();
    console.log(okPayload.message);
} else {
    throw new Error(`Unexpected response: ${JSON.stringify(response.body)}`);
}
```

For more concrete usage examples, [see the tests](https://github.com/Telepact/telepact/blob/main/test/lib/ts/src/main.ts).



---

## Telepact Library for Python

### Installation

```
pip install telepact
```

### Usage

API:

```json
[
    {
        "fn.greet": {
            "subject": "string"
        },
        "->": {
            "Ok_": {
                "message": "string"
            }
        }
    }
]
```

Server:

```py

files = TelepactSchemaFiles('/directory/containing/api/files')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)

async def handler(request_message: 'Message') -> 'Message':
    function_name = request_message.body.keys[0]
    arguments = request_message.body[function_name]

    try:
        # Early in the handler, perform any pre-flight "middleware" operations, such as
        # authentication, tracing, or logging.
        log.info("Function started", {'function': function_name})

        # Dispatch request to appropriate function handling code.
        # (This example uses manual dispatching, but you can also use a more advanced pattern.)
        if function_name == 'fn.greet':
            subject = arguments['subject']
            return Message({}, {'Ok_': {'message': f'Hello {subject}!'}})

        raise Exception('Function not found')
    finally:
        # At the end the handler, perform any post-flight "middleware" operations
        log.info("Function finished", {'function': function_name})


options = Server.Options()
server = Server(schema, handler, options)


# Wire up request/response bytes from your transport of choice
async def transport_handler(request_bytes: bytes) -> bytes:
    response = await server.process(request_bytes)
    return response.bytes

transport.receive(transport_handler)
```

Client:

```py
async def adapter(m: Message, s: Serializer) -> Message:
    request_bytes = s.serialize(m)

    # Wire up request/response bytes to your transport of choice
    response_bytes = await transport.send(request_bytes)

    return s.deserialize(response_bytes)

options = Client.Options()
client = Client(adapter, options)

# Inside your async application code:
request = Message({}, {'fn.greet': {'subject': 'World'}})
response = await client.request(request)
if response.get_body_target() == 'Ok_':
    ok_payload = response.get_body_payload()
    print(ok_payload['message'])
else:
    raise RuntimeError(f"Unexpected response: {response.body}")
```

For more concrete usage examples,
[see the tests](https://github.com/Telepact/telepact/blob/main/test/lib/py/telepact_test/test_server.py).


---

## Telepact Library for Java

### Installation
```xml
<dependency>
    <groupId>io.github.telepact</groupId>
    <artifactId>telepact</artifactId>
</dependency>
```

### Usage

API:
```json
[
    {
        "fn.greet": {
            "subject": "string"
        },
        "->": {
            "Ok_": {
                "message": "string"
            }
        }
    }
]
```

Server:
```java
var files = new TelepactSchemaFiles("./directory/containing/api/files");
var schema = TelepactSchema.fromFilesJsonMap(files.filenamesToJson);
Function<Message, Message> handler = (requestMessage) -> {
    var functionName = requestMessage.body.keySet().stream().findAny();
    var arguments = (Map<String, Object>) requestMessage.body.get(functionName);

    try {
        // Early in the handler, perform any pre-flight "middleware" operations, such as
        // authentication, tracing, or logging.
        log.info("Function started", Map.of("function", functionName));

        // Dispatch request to appropriate function handling code.
        // (This example uses manual dispatching, but you can also use a more advanced pattern.)
        if (functionName.equals("fn.greet")) {
            var subject = (String) arguments.get("subject");
            return new Message(Map.of(), Map.of("Ok_", Map.of("message": "Hello %s!".formatted(subject))));
        }

        throw new RuntimeException("Function not found");
    } finally {
        // At the end the handler, perform any post-flight "middleware" operations
        log.info("Function finished", Map.of("function", functionName));
    }
};
var options = new Server.Options();
var server = new Server(schema, handler, options);


// Wire up request/response bytes from your transport of choice
transport.receive((requestBytes) -> {
    var response = server.process(requestBytes);
    return response.bytes;
});
```

Client:
```java
BiFunction<Message, Serializer, Future<Message>> adapter = (m, s) -> {
    return CompletableFuture.supplyAsync(() -> {
        var requestBytes = s.serialize(m);
        
        // Wire up request/response bytes to your transport of choice
        var responseBytes = transport.send(requestBytes);
        
        return s.deserialize(responseBytes);
    });
};
var options = new Client.Options();
var client = new Client(adapter, options);

var request = new Message(
    Map.of(),
    Map.of("fn.greet", Map.of("subject", "World"))
);
var response = client.request(request);
if ("Ok_".equals(response.getBodyTarget())) {
    var okPayload = response.getBodyPayload();
    System.out.println(okPayload.get("message"));
} else {
    throw new RuntimeException("Unexpected response: " + response.body);
}
```

For more concrete usage examples, [see the tests](https://github.com/Telepact/telepact/blob/main/test/lib/java/src/main/java/telepacttest/Main.java).

---

# Telepact CLI

The CLI is a tool for various development jobs, such as fetching API schemas,
generating code, and starting up mock servers for testing purposes.

## Installation

```
pipx install telepact-cli
```

## Usage

```
telepact --help
```



---

# Telepact Console

The Console is a debugging tool that allows you to easily connect to your
running Telepact server, visualize your API with interactive documentation, and
submit live requests to your server.

## Installation

```
npm install -g telepact-console
```

## Usage

```
npx telepact-console -p 8080
```

Then you can access the UI in your browser at http://localhost:8080.

## Docker

The Console is also available as a docker image, which can be installed directly from
[Releases](https://github.com/Telepact/telepact/releases). You can copy the link
for the Console from the release assets.

Example:

```
curl -L -o telepact-docker.tar.gz https://github.com/Telepact/telepact/releases/download/1.0.0-alpha.102/docker-image-telepact-console-1.0.0-alpha.102.tar.gz
docker load < telepact-docker.tar.gz
```

Starting the docker container:

```
docker run -p 8080:8080 telepact-console:1.0.0-alpha.102
```

For a more concrete usage example, see
[self-hosting example](https://github.com/Telepact/telepact/blob/main/test/console-self-hosted/).



---

# Telepact Prettier Plugin

Keep your Telepact API schemas well-formatted (especially the docstrings) using
this prettier plugin.

## Installation
```
npm install prettier-plugin-telepact
```

## Usage

This plugin requires prettier configuration, for example, in the `.prettierrc` file:
```json
{
    "plugins": ["prettier-plugin-telepact"],
    "overrides": [
        {
            "files": "*.telepact.json",
            "options": {
                "parser": "telepact-parse"
            }
        }
    ]
}
```

For a real-use example, see
[example prettier config file](https://github.com/Telepact/telepact/blob/main/.prettierrc).



---

# Appendix

## internal-telepact-json

```json
[
    {
        "///": " Ping the server. ",
        "fn.ping_": {},
        "->": [
            {
                "Ok_": {}
            }
        ],
        "_errors": "^errors\\.Validation_$"
    },
    {
        "///": " Get the telepact `schema` of this server. ",
        "fn.api_": {},
        "->": [
            {
                "Ok_": {
                    "api": [{"string": "any"}]
                }
            }
        ],
        "_errors": "^errors\\.Validation_$"
    },
    {
        "_ext.Select_": {}
    },
    {
        "///": " The `@time_` header indicates the request timeout honored by the client. ",
        "headers.Time_": {
            "@time_": "integer"
        },
        "->": {}
    },
    {
        "///": [
            " If `@unsafe_` is set to `true`, response validation by the server will be       ",
            " disabled. The server will the client-provided the value of `@unsafe_` header    ",
            " in the response.                                                                "
        ],
        "headers.Unsafe_": {
            "@unsafe_": "boolean"
        },
        "->": {
            "@unsafe_": "boolean"
        }
    },
    {
        "///": " The `@select_` header is used to select fields from structs. ",
        "headers.Select_": {
            "@select_": "_ext.Select_"
        },
        "->": {}
    },
    {
        "///": [
            " The `@bin_` header indicates the valid checksums of binary encodings            ",
            " negotiated between the client and server. If the client sends a `@bin_` header  ",
            " with any value, the server will respond with a `@bin_` header with an array     ",
            " containing the currently supported binary encoding checksum. If te client's     ",
            " provided checksum does not match the server's checksum, the server will also    ",
            " send an `@enc_` header containing the binary encoding, which is a map of field  ",
            " names to field ids. The response body may also be encoded in binary.            ",
            "                                                                                 ",
            " The `@pac_` header can also be used to indicate usage of 'packed' binary        ",
            " encoding strategy. If the client submits a `@pac_` header with a `true` value,  ",
            " the server will respond with a `@pac_` header with a `true` value.              "
        ],
        "headers.Binary_": {
            "@bin_": ["integer"],
            "@pac_": "boolean"
        },
        "->": {
            "@bin_": ["integer"],
            "@enc_": {"string": "integer"},
            "@pac_": "boolean"
        }
    },
    {
        "///": " The `@warn_` header is used to send warnings to the client. ",
        "headers.Warning_": {},
        "->": {
            "@warn_": ["any"]
        }
    },
    {
        "///": [
            " The `@id_` header is used to correlate requests and responses. The server will  ",
            " reflect the client-provided `@id_` header as-is.                                "
        ],
        "headers.Id_": {
            "@id_": "any"
        },
        "->": {
            "@id_": "any"
        }
    },
    {
        "///": " A type. ",
        "union.Type_": [
            {
                "Null": {}
            },
            {
                "Boolean": {}
            },
            {
                "Integer": {}
            },
            {
                "Number": {}
            },
            {
                "String": {}
            },
            {
                "Array": {}
            },
            {
                "Object": {}
            },
            {
                "Any": {}
            },
            {
                "Base64String": {}
            },
            {
                "Bytes": {}
            },
            {
                "Unknown": {}
            }
        ]
    },
    {
        "///": " A reason for the validation failure in the body. ",
        "union.ValidationFailureReason_": [
            {
                "TypeUnexpected": {
                    "expected": "union.Type_",
                    "actual": "union.Type_"
                }
            },
            {
                "NullDisallowed": {}
            },
            {
                "ObjectKeyDisallowed": {}
            },
            {
                "RequiredObjectKeyPrefixMissing": {
                    "prefix": "string"
                }
            },
            {
                "ArrayElementDisallowed": {}
            },
            {
                "NumberOutOfRange": {}
            },
            {
                "ObjectSizeUnexpected": {
                    "expected": "integer",
                    "actual": "integer"
                }
            },
            {
                "ExtensionValidationFailed": {
                    "reason": "string",
                    "data!": {"string": "any"}
                }
            },
            {
                "ObjectKeyRegexMatchCountUnexpected": {
                    "regex": "string",
                    "expected": "integer",
                    "actual": "integer",
                    "keys": ["string"]
                }
            },
            {
                "RequiredObjectKeyMissing": {
                    "key": "string"
                }
            },
            {
                "FunctionUnknown": {}
            }
        ]
    },
    {
        "///": " A parse failure. ",
        "union.ParseFailure_": [
            {
                "IncompatibleBinaryEncoding": {}
            },
            {
                "///": " The binary decoder encountered a field id that could not be mapped to a key. ",
                "BinaryDecodeFailure": {}
            },
            {
                "JsonInvalid": {}
            },
            {
                "ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject": {}
            },
            {
                "ExpectedJsonArrayOfTwoObjects": {}
            }
        ]
    },
    {
        "///": " A validation failure located at a `path` explained by a `reason`. ",
        "struct.ValidationFailure_": {
            "path": ["any"],
            "reason": "union.ValidationFailureReason_"
        }
    },
    {
        "///": " A standard error. ",
        "errors.Validation_": [
            {
                "///": " The server implementation raised an unknown error. ",
                "ErrorUnknown_": {}
            },
            {
                "///": " The headers on the request are invalid. ",
                "ErrorInvalidRequestHeaders_": {
                    "cases": ["struct.ValidationFailure_"]
                }
            },
            {
                "///": " The body on the request is invalid. ",
                "ErrorInvalidRequestBody_": {
                    "cases": ["struct.ValidationFailure_"]
                }
            },
            {
                "///": " The headers on the response are invalid. ",
                "ErrorInvalidResponseHeaders_": {
                    "cases": ["struct.ValidationFailure_"]
                }
            },
            {
                "///": " The body that the server attempted to put on the response is invalid. ",
                "ErrorInvalidResponseBody_": {
                    "cases": ["struct.ValidationFailure_"]
                }
            },
            {
                "///": " The request could not be parsed as a telepact Message. ",
                "ErrorParseFailure_": {
                    "reasons": ["union.ParseFailure_"]
                }
            }
        ]
    }
]
```

## auth-telepact-json

```json
[
    {
        "///": [
            " The `@auth_` header is the conventional location for sending credentials to     ",
            " the server for the purpose of authentication and authorization.                 "
        ],
        "headers.Auth_": {
            "@auth_": "struct.Auth_"
        },
        "->": {}
    },
    {
        "///": " A standard error. ",
        "errors.Auth_": [
            {
                "///": " The credentials in the `_auth` header were missing or invalid. ",
                "ErrorUnauthenticated_": {
                    "message!": "string"
                }
            },
            {
                "///": " The credentials in the `_auth` header were insufficient to run the function. ",
                "ErrorUnauthorized_": {
                    "message!": "string"
                }
            }
        ]
    }
]
```

## mock-internal-telepact-json

```json
[
    {
        "///": " A stubbed result for matching input. ",
        "_ext.Stub_": {}
    },
    {
        "///": " A call of a function. ",
        "_ext.Call_": {}
    },
    {
        "///": " The number of times a function is allowed to be called. ",
        "union.CallCountCriteria_": [
            {
                "Exact": {
                    "times": "integer"
                }
            },
            {
                "AtMost": {
                    "times": "integer"
                }
            },
            {
                "AtLeast": {
                    "times": "integer"
                }
            }
        ]
    },
    {
        "///": " Possible causes for a mock verification to fail. ",
        "union.VerificationFailure_": [
            {
                "TooFewMatchingCalls": {
                    "wanted": "union.CallCountCriteria_",
                    "found": "integer",
                    "allCalls": ["_ext.Call_"]
                }
            },
            {
                "TooManyMatchingCalls": {
                    "wanted": "union.CallCountCriteria_",
                    "found": "integer",
                    "allCalls": ["_ext.Call_"]
                }
            }
        ]
    },
    {
        "///": [
            " Create a function stub that will cause the server to return the `stub` result   ",
            " when the `stub` argument matches the function argument on a request.            ",
            "                                                                                 ",
            " If `ignoreMissingArgFields` is `true`, then the server will skip field          ",
            " omission validation on the `stub` argument, and the stub will match calls       ",
            " where the given `stub` argument is Exactly a json sub-structure of the request  ",
            " function argument.                                                              ",
            "                                                                                 ",
            " If `generateMissingResultFields` is `true`, then the server will skip field     ",
            " omission validation on the `stub` result, and the server will generate the      ",
            " necessary data required to make the `result` pass on response validation.       "
        ],
        "fn.createStub_": {
            "stub": "_ext.Stub_",
            "strictMatch!": "boolean",
            "count!": "integer"
        },
        "->": [
            {
                "Ok_": {}
            }
        ],
        "_errors": "^errors\\.Validation_$"
    },
    {
        "///": [
            " Verify a call was made with this mock that matches the given `call` and         ",
            " `multiplicity` criteria. If `allowPartialArgMatch` is supplied as `true`, then  ",
            " the server will skip field omission validation, and match calls where the       ",
            " given `call` argument is Exactly a json sub-structure of the actual argument.   "
        ],
        "fn.verify_": {
            "call": "_ext.Call_",
            "strictMatch!": "boolean",
            "count!": "union.CallCountCriteria_"
        },
        "->": [
            {
                "Ok_": {}
            },
            {
                "ErrorVerificationFailure": {
                    "reason": "union.VerificationFailure_"
                }
            }
        ],
        "_errors": "^errors\\.Validation_$"
    },
    {
        "///": [
            " Verify that no interactions have occurred with this mock or that all            ",
            " interactions have been verified.                                                "
        ],
        "fn.verifyNoMoreInteractions_": {},
        "->": [
            {
                "Ok_": {}
            },
            {
                "ErrorVerificationFailure": {
                    "additionalUnverifiedCalls": ["_ext.Call_"]
                }
            }
        ],
        "_errors": "^errors\\.Validation_$"
    },
    {
        "///": " Clear all stub conditions. ",
        "fn.clearStubs_": {},
        "->": [
            {
                "Ok_": {}
            }
        ],
        "_errors": "^errors\\.Validation_$"
    },
    {
        "///": " Clear all call data. ",
        "fn.clearCalls_": {},
        "->": [
            {
                "Ok_": {}
            }
        ],
        "_errors": "^errors\\.Validation_$"
    },
    {
        "///": " Set the seed of the random generator. ",
        "fn.setRandomSeed_": {
            "seed": "integer"
        },
        "->": [
            {
                "Ok_": {}
            }
        ],
        "_errors": "^errors\\.Validation_$"
    },
    {
        "errors.Mock_": [
            {
                "///": " The mock could not return a result due to no matching stub being available. ",
                "ErrorNoMatchingStub_": {}
            }
        ]
    }
]
```

