# Schema Writing Guide

## Type Expression
Types are expressed with a non-empty array of strings.

Type Expression | Example allowed JSON values | Example disalowed JSON values
--- | --- | ---
`["boolean"]` | `true`, `false` | `null`, `0`
`["integer"]` | `1`, `0`, `-1` | `null`, `0.1`
`["number"]` | `0.1`, `-0.1` | `null`, `"0"`
`["string"]` | `""`, `"text"` | `null`, `0`
`["array", ["boolean"]]` | `[]`, `[true, false]` | `null`, `0`, `{}`
`["object", ["integer"]]` | `{}`, `{"key1": 0, "key2": 1}` | `null`, `0`, `[]`
`["any"]` | `false`, `0`, `0.1`, `""`, `[]`, `{}` | `null`

### Nullability
The `?` symbol can be appended to type strings to indicate nullability.

Type Expression | Example allowed JSON values | Example disalowed JSON values
--- | --- | ---
`["boolean?"]` | `null`, `true`, `false` | `0`
`["integer?"]` | `null`, `1`, `0`, `-1` | `0.1`
`["number?"]` | `null`, `0.1`, `-0.1` | `"0"`
`["string?"]` | `null`, `""`, `"text"` | `0`
`["array?", ["boolean?"]]` | `null`, `[]`, `[true, false]` | `0`, `{}`
`["object?", ["integer?"]]` | `null`, `{}`, `{"key1": 0, "key2": 1}` | `0`, `[]`
`["any?"]` | `null`, `false`, `0`, `0.1`, `""`, `[]`, `{}` | (none)

## Definitions
A Telepact Schema is an array of the following definition patterns:
- struct
- union
- function
- errors
- headers

### Struct Definition
Type expressions can be encased in a structured object (product) type. They can
then be used in any type expression.

```json
[
  {
    "struct.ExampleStruct1": {
      "field": ["boolean"],
      "anotherField": ["array", ["string"]]
    }
  },
  {
    "struct.ExampleStruct2": {
      "optionalField!": ["boolean"],
      "anotherOptionalField!": ["integer"]
    }
  }
]
```

Type Expression | Example allowed JSON values | Example disallowed JSON values
--- | --- | ---
`["struct.ExampleStruct1"]` | `{"field": true, "anotherField": ["text1", "text2"]}` | `null`, `{}` 
`["struct.ExampleStruct2"]` | `{"optionalField!": true}`, `{}` | `null`, `{"wrongField": true}`

### Union
Type expressions can also be encased in tagged structered object (sum) type. They
too can be used in any type expression.

At least one tag is required.

```json
[
  {
    "union.ExampleUnion1": [
      {
        "Tag": {
          "field": ["integer"]
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
          "optionalField!": ["string"]
        }
      }
    ]
  }
]
```

Type Expression | Example allowed JSON values | Example disallowed JSON values
--- | --- | ---
`["struct.ExampleUnion1"]` | `{"Tag": {"field": 0}}`, `{"EmptyTag": {}}` | `null`, `{}`
`["struct.ExampleUnion2"]` | `{"Tag": {"optionalField!": "text"}}`, `{"Tag": {}}` | `null`, `{}`

### Function
Request-Response semantics can be defined with functions. A function is a combination
of a argument struct and a result union. The result union requires at least the `Ok_` tag.
By convention, all non-`Ok_` tags are considered as errors.

Clients interact with servers through functions; the client submits JSON data valid
against the function arugument struct definition, and the server responds with JSON
data valid against the function result union.

When referenced as a type in type expressions, the result union is unused.

```json
[
  {
    "fn.exampleFunction1": {
      "field": ["integer"],
      "optionalField!": ["string"]
    },
    "->": [
      {
        "Ok_": {
          "field": ["boolean"]
        }
      }
    ]
  },
  {
    "fn.exampleFunction2": {},
    "->": [
      {
        "Ok_": {},
      },
      {
        "Error": {
          "field": ["string"]
        }
      }
    ]
  }  
]
```

Request | Example Response
--- | ---
`[{}, {"fn.exampleFunction1": {"field": 1}}]` | `[{}, {"Ok_": {"field": true}}]`
`[{}, {"fn.exampleFunction2": {}}]` | `[{}, {"Error": {"field": "text"}}]`

Type Expression | Example allowed JSON values | Example disallowed JSON values
--- | --- | ---
`["fn.exampleFunction1"]` | `{"field": 0}`, `{"field": 1, "optionalField!": "text"}` | `null`, `{}`
`["fn.exampleFunction2"]` | `{}` | `null`, `{"wrongField": 0}`

### Errors
Errors definitions are similar to unions, except that the tags are automatically added to the
result union of all user-defined functions. Errors definitions cannot be used in type 
expressions.

```json
[
  {
    "errors.ExampleErrors1": [
      {
        "Error1": {
          "field": ["integer"]
        }
      },
      {
        "Error2": {}
      }
    ]
  }
]
```

With this error definition, the functions above would automatically be given these errors.
(Note, the following example illustrates the effect of the errors definition at schema load time; the original schema is not re-written.)

```json
[
  {
    "fn.exampleFunction1": {
      "field": ["integer"],
      "optionalField!": ["string"]
    },
    "->": [
      {
        "Ok_": {
          "field": ["boolean"]
        }
      },
      {
        "Error1": {
          "field": ["integer"]
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
        "Ok_": {},
      },
      {
        "Error": {
          "field": ["string"]
        }
      },
      {
        "Error1": {
          "field": ["integer"]
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
Headers definitions are similar to function definitions in that correlate to the
request/response semantics, but only with respect to the headers object on the
Telepact message. Both the request and reply definitions resemble struct definitions,
with a few exceptions:
- all header fields must be prepended with `@`
- all header fields are implicitly optional
- additional header fields not specified in the definition will be allowed during validation

Headers definitions cannot be used in type expressions.

```json
[
  {
    "headers.Example": {
      "@requestHeader": ["boolean"],
      "@anotherRequestHeader": ["integer"]
    },
    "->": {
      "@responseHeader": ["string"]
    }
  }
]
```

Request | Example Response
--- | ---
`[{"@requestHeader": true}, {"fn.ping_": {}}]` | `[{"@responseHeader": "text"}, {"Ok_": {}}]`
`[{"@anotherRequestHeader": true}, {"fn.ping_": {}}]` | `[{"@unspecifiedHeader": true}, {"Ok_": {}}]`

Example Invalid Request | Example Invalid Response
--- | ---
`[{"@requestHeader": 1}, {"fn.ping_": {}}]` | `[{"@responseHeader": 1}, {"Ok_": {}}]`

