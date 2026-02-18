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

