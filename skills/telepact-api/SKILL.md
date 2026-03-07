---
name: telepact-api
description: Read, draft, and implement Telepact APIs.
license: Apache-2.0
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

These innovations allow Telepact to design for the minimalist consumer while
giving clients the option to enrich the consumer experience by:
- Selecting less fields to reduce response sizes
- Generating code to increase type safety
- Using binary serialization to reduce request/response sizes

# It's just JSON
No query params. No binary field ids. No required client libraries.

It's just JSON in, and JSON out.

Schema:
```json
[{"fn.helloWorld": {}, "->": [{"Ok_": {"msg": "string"}}]}]
```
Request:
```json
[{}, {"fn.helloWorld":{}}]
```
Response:
```json
[{}, {"Ok_": {"msg": "Hello world!"}}]
```

Check out the [full-stack example](./references/example.md).

# Explore

To learn how to write Telepact APIs, see the [API Schema Guide](#schema-writing-guide).
A [JSON Schema](./references/json-schema.json) is available for validation.

To learn how to serve a Telepact API, see the specific library docs:
- [Typescript](./references/ts.md)
- [Python](./references/py.md)
- [Java](./references/java.md)
- [Go](./references/go.md)

For development assistance, see the SDK tool docs:
- [CLI](#telepact-cli)
    - Conveniently retreive API schemas from running live Telepact servers, and
      use schemas to create mock servers and generate code bindings, all from
      the command line
- [Browser Console](./references/console.md)
    - Develop against a live Telepact server by reading rendered docs, drafting
      requests, and submitting live requests with json-friendly editors
- [Prettier Plugin](./references/prettier.md)
    - Consistently format your Telepact api schemas, especially the doc-strings

Find the latest versions of all libraries and sdks [here](#versions).

For further reading, see [Motivation](./references/motivation.md).

Telepact does have a few unorthodox design decisions. To be best informed,
you should read the explanations in [the FAQ](#faq).

# Licensing

Telepact is licensed under the Apache License, Version 2.0. See
[LICENSE](./references/LICENSE) for the full license text. See [NOTICE](./references/NOTICE) for
additional information regarding copyright ownership.

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

#### Don't over-error

**NOTE**: API designers should be careful to avoid using errors definitions to abstract
"reusable" errors. Errors definitions are only intended for systemic server
errors that could be encountered by any function.

For instance, in Telepact, there is no standard "Not found" error, because Telepact
favors expressive data, such as using an empty optional field to replace conventional
"Not found" patterns.

❌ Bad:
```json
[
    {
        "errors.GeneralErrors": [
            {
                "NotFound": {}
            }
        ]
    },
    {
        "fn.exampleFunction": {},
        "->": [
            {
                "Ok_": {
                    "result": "string"
                }
            }
        ]
    }
]
```

✅ Good:
```json
[
    {
        "fn.exampleFunction": {},
        "->": [
            {
                "Ok_": {
                    "result!": "string"
                }
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

The `fn.api_` helper returns the user-facing schema by default. Pass
`{"includeInternal!": true}` to include these standard Telepact definitions in
the response. For mock servers, this expanded response also includes the
bundled mock schema definitions.

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

You can find all mock definitions
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

## Appendix

### auth-telepact-json

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

### internal-telepact-json

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
        "///": " Get the telepact `schema` of this server. Set `includeInternal` to `true` to include Telepact internal definitions. ",
        "fn.api_": {
            "includeInternal!": "boolean"
        },
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

### mock-internal-telepact-json

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

# FAQ

## Who exactly needs to use Telepact libraries?

Telepact boasts a flexible development environment for clients, who are
allowed to bring as much or as little Telepact tooling as they like, including
no tooling at all in favor of industry standard JSON and network libraries.

The server, however, MUST use a Telepact library to serve its Telepact API.
Doing so ensures a rich Telepact ecosystem for developers and clients,
including features such as automatic API retrieval for mocking, documentation
browsing using the console, request validation, opt-in binary, and response
field selection.

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

## Why do optional fields keep the `!` symbol in the request/response payloads?

If a field is marked as optional in the schema, such as `"field!": "integer"`,
it will keep that `!` symbol on live payloads, such as `"field!": 42`.

This pattern serves two purposes (1) to keep the schema and live payloads as
similar as possible, and (2) to alert code writers of the optional edge case.
If a client encounters something like `response['field!']` in code, the `!`
immediately alerts the code reader that an `undefined`-like value might be
returned from the code expression.

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

# Versions

| Kind | Package | Registry | Version |
|---|---|---|---|
| Library (Go) | `github.com/telepact/telepact/lib/go` | Go module (proxy.golang.org) | `v1.0.0-alpha.181` |
| Library (Java) | `io.github.telepact:telepact` | Maven Central | `1.0.0-alpha.185` |
| Library (Python) | `telepact` | PyPI | `1.0.0-alpha.185` |
| Library (TypeScript) | `telepact` | npm | `1.0.0-alpha.185` |
| SDK (CLI) | `telepact-cli` | PyPI | `1.0.0-alpha.191` |
| SDK (Console) | `telepact-console` | npm | `1.0.0-alpha.192` |
| SDK (Prettier) | `prettier-plugin-telepact` | npm | `1.0.0-alpha.185` |

# Telepact CLI

The CLI is a tool for various development jobs, such as fetching API schemas,
generating code, and starting up mock servers for testing purposes.

## Installation

```
pipx install telepact-cli
```

## Usage

### `telepact --help`
```
Usage: telepact [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  codegen      Generate code bindings for a Telepact API schema.
  compare      Compare two Telepact API schemas for backwards compatibility.
  demo-server  Start a demo Telepact server.
  fetch        Fetch a Telepact API schema to store locally.
  mock         Start a mock server for a Telepact API schema.
```

### `telepact codegen --help`
```
Usage: telepact codegen [OPTIONS]

  Generate code bindings for a Telepact API schema.

Options:
  --schema-http-url TEXT  telepact schema directory
  --schema-dir TEXT       telepact schema directory
  --lang TEXT             Language target (one of "java", "py", "ts", or "go")
                          [required]
  --out TEXT              Output directory  [required]
  --package TEXT          Java package (use if --lang is "java")
  --help                  Show this message and exit.
```

### `telepact compare --help`
```
Usage: telepact compare [OPTIONS]

  Compare two Telepact API schemas for backwards compatibility.

Options:
  --new-schema-dir TEXT  New telepact schema directory  [required]
  --old-schema-dir TEXT  Old telepact schema directory  [required]
  --help                 Show this message and exit.
```

### `telepact fetch --help`
```
Usage: telepact fetch [OPTIONS]

  Fetch a Telepact API schema to store locally.

Options:
  --http-url TEXT    HTTP URL of a Telepact API  [required]
  --output-dir TEXT  Directory of Telepact schemas  [required]
  --help             Show this message and exit.
```

### `telepact mock --help`
```
Usage: telepact mock [OPTIONS]

  Start a mock server for a Telepact API schema.

Options:
  --http-url TEXT                 HTTP URL of a Telepact API
  --dir TEXT                      Directory of Telepact schemas
  --port INTEGER                  Port to run the mock server on
  --path TEXT                     Path to expose the mock API (default: /api)
  --generated-collection-length-min INTEGER
                                  Minimum length of generated collections
  --generated-collection-length-max INTEGER
                                  Maximum length of generated collections
  --disable-optional-field-generation
                                  Disable generation of optional fields
                                  (enabled by default)
  --disable-message-response-generation
                                  Disable generation of message responses
                                  (enabled by default)
  --disable-random-optional-field-generation
                                  Disable randomization of optional field
                                  generation (enabled by default)
  --help                          Show this message and exit.
```

NOTE: The `mock` command is an empowering development tool for clients. You do
not need to develop against a live server; you can use the `mock` command to
set up a "middle-man" server that will validate requests for schema compliance
and return schema-compliant auto-generated responses (which can be overrideen
with manual stubs if desired.)