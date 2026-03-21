# Schema Writing Guide

This guide explains how to understand and write Telepact schema files.

For normal checked-in authoring, prefer `*.telepact.yaml`. YAML is easier to
read at rest, especially for multi-line `///` docstrings. `*.telepact.json` is
still valid and remains the canonical lowered and wire-aligned representation.

The schema itself is still JSON-shaped. In this guide, checked-in schema-file
examples use YAML, while exact type-expression fragments and wire examples may
still use JSON syntax where that is more precise.

## Schema Directories

When a Telepact runtime or tool accepts a schema directory, it loads the
immediate files in that directory as one schema.

Rules:

- supported file names are `*.telepact.yaml` and `*.telepact.json`
- YAML and JSON files may be mixed in the same directory
- subdirectories are not part of the schema and are rejected with `DirectoryDisallowed`
- file order does not affect schema semantics
- cross-file collisions are handled exactly as if all definitions had been
  authored in one file

In practice, you can think of a schema directory as an unordered union of the
supported schema files directly inside that directory.

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

```yaml
- struct.ExampleStruct1:
    field: boolean
    anotherField: ["string"]
- struct.ExampleStruct2:
    optionalField!: boolean
    anotherOptionalField!: integer
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

```yaml
- union.ExampleUnion1:
    - Tag:
        field: integer
    - EmptyTag: {}
- union.ExampleUnion2:
    - Tag:
        optionalField!: string
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

```yaml
- fn.exampleFunction1:
    field: integer
    optionalField!: string
  ->:
    - Ok_:
        field: boolean
- fn.exampleFunction2: {}
  ->:
    - Ok_: {}
    - Error:
        field: string
```

| Example Request                               | Example Response                     |
| --------------------------------------------- | ------------------------------------ |
| `[{}, {"fn.exampleFunction1": {"field": 1}}]` | `[{}, {"Ok_": {"field": true}}]`     |
| `[{}, {"fn.exampleFunction2": {}}]`           | `[{}, {"Error": {"field": "text"}}]` |

| Type Expression         | Example allowed JSON values                                                          | Example disallowed JSON values                 |
| ----------------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------- |
| `"fn.exampleFunction1"` | `{"fn.exampleFunction1": {"field": 0}}`, `{"fn.exampleFunction1": {"field": 1, "optionalField!": "text"}}` | `null`, `{}`, `{"field": 0}`                 |
| `"fn.exampleFunction2"` | `{"fn.exampleFunction2": {}}`                                                       | `null`, `{"wrongField": 0}`, `{}`            |

### Errors

Errors definitions are similar to unions, except that the tags are automatically
added to the result union of all user-defined functions. Errors definitions
cannot be used in type expressions.

```yaml
- errors.ExampleErrors1:
    - Error1:
        field: integer
    - Error2: {}
```

For example, if placed in the same schema, the above error definition would
apply the errors `Error1` and `Error2` to both the `fn.exampleFunction1` and
`fn.exampleFunction2` functions from the previous section, as indicated below
(Note, the following example only illustrates the effect of the errors
definition at schema load time; the original schema is not re-written.)

```yaml
- fn.exampleFunction1:
    field: integer
    optionalField!: string
  ->:
    - Ok_:
        field: boolean
    - Error1:
        field: integer
    - Error2: {}
- fn.exampleFunction2: {}
  ->:
    - Ok_: {}
    - Error:
        field: string
    - Error1:
        field: integer
    - Error2: {}
```

#### Don't over-error

**NOTE**: API designers should be careful to avoid using errors definitions to abstract
"reusable" errors. Errors definitions are only intended for systemic server
errors that could be encountered by any function.

For instance, in Telepact, there is no standard "Not found" error, because Telepact
favors expressive data, such as using an empty optional field to replace conventional
"Not found" patterns.

❌ Bad:
```yaml
- errors.GeneralErrors:
    - NotFound: {}
- fn.exampleFunction: {}
  ->:
    - Ok_:
        result: string
```

✅ Good:
```yaml
- fn.exampleFunction: {}
  ->:
    - Ok_:
        result!: string
```

### Headers

Headers definitions are similar to function definitions in that they correlate
to the request/response semantics, but only with respect to the headers object
on the Telepact message. Both the request and response definitions resemble
struct definitions, with a few exceptions:

-   all header fields must be prepended with `@`
-   all header fields are implicitly optional
-   header fields must not use the `!` suffix because optionality is already
    implied for all headers
-   additional header fields not specified in the definition will be allowed
    during validation

Header names therefore follow the pattern `^@[a-z][a-zA-Z0-9_]*$`.

Headers definitions cannot be used in type expressions.

```yaml
- headers.Example:
    "@requestHeader": boolean
    "@anotherRequestHeader": integer
  ->:
    "@responseHeader": string
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

```yaml
- ///: A struct that contains a `field`.
  struct.ExampleStruct:
    field: boolean
- struct.ExampleUnion:
    - ///: The default `Tag` that contains a `field`.
      Tag:
        field: integer
```

Prefer YAML when multi-line docstrings are desired.

```yaml
- ///: |
    A struct that contains a field.

    Fields:
      - `field` (type: `boolean`)
  struct.ExampleStruct:
    field: boolean
```

## Automatic Definitions

Some definitions are automatically appended to your schema at runtime.

### Standard Definitions

Standard definitions include utility functions, like `fn.ping_`, and common
errors, like `ErrorInvalidRequest` and `ErrorUnknown_`. These are always
included and cannot be turned off.

The `fn.api_` helper returns the user-facing schema by default. Pass
`{"includeInternal!": true}` to include these standard Telepact definitions in
the response. Pass `{"includeExamples!": true}` to attach deterministic example
payloads to each returned schema entry. For mock servers, the expanded response
also includes the bundled mock schema definitions.

You can find all standard definitions
[here](https://raw.githubusercontent.com/Telepact/telepact/refs/heads/main/common/internal.telepact.yaml).

### Auth Definitions

Auth definitions include the `@auth_` header and the `ErrorUnauthenticated_` and
`ErrorUnauthorized_` errors. These are included conditionally if the API writer
defines a `struct.Auth_` definition in their schema, for the auth header
definition data type references it, as in `"@auth_": "struct.Auth_"`.

API writiers are strongly encouraged to place all auth-related data into the
standard `struct.Auth_` struct, as the `@auth_` header is treated with greater
sensitivity throughout the Telepact ecosystem.

You can find details about auth definitions
[here](https://raw.githubusercontent.com/Telepact/telepact/refs/heads/main/common/auth.telepact.yaml).

### Mock Definitions

Mock definitions include mocking functions, like `fn.createStub_` and
`fn.verify_` for use in tests. These definitions are included if the API is
served with a `MockServer` rather than a `Server` in the Telepact server-side
library.

These schemas also include reserved `_ext.*_` extension types. Unlike ordinary
schema definitions, extension types are placeholders whose actual validation
rules come from Telepact runtime behavior and surrounding schema context.

You can find all mock definitions
[here](https://raw.githubusercontent.com/Telepact/telepact/refs/heads/main/common/mock-internal.telepact.yaml).
There is also a guide to Telepact extension types, including mock extensions,
[here](https://raw.githubusercontent.com/Telepact/telepact/main/doc/extensions.md).

## Full Example

### Schema

```yaml
- ///: A calculator app that provides basic math computation capabilities.
  info.Calculator: {}
- ///: A function that adds two numbers.
  fn.add:
    x: number
    y: number
  ->:
    - Ok_:
        result: number
- ///: A value for computation that can take either a constant or variable form.
  union.Value:
    - Constant:
        value: number
    - Variable:
        name: string
- ///: A basic mathematical operation.
  union.Operation:
    - Add: {}
    - Sub: {}
    - Mul: {}
    - Div: {}
- ///: A mathematical variable represented by a `name` that holds a certain `value`.
  struct.Variable:
    name: string
    value: number
- ///: Save a set of variables as a dynamic map of variable names to their value.
  fn.saveVariables:
    variables: {"string": "number"}
  ->:
    - Ok_: {}
- ///: Compute the `result` of the given `x` and `y` values.
  fn.compute:
    x: union.Value
    y: union.Value
    op: union.Operation
  ->:
    - Ok_:
        result: number
    - ErrorCannotDivideByZero: {}
- ///: Export all saved variables, up to an optional `limit`.
  fn.exportVariables:
    limit!: integer
  ->:
    - Ok_:
        variables: ["struct.Variable"]
- ///: A function template.
  fn.getPaperTape: {}
  ->:
    - Ok_:
        tape: ["struct.Computation"]
- ///: A computation.
  struct.Computation:
    user: string?
    firstOperand: union.Value
    secondOperand: union.Value
    operation: union.Operation
    result: number?
    successful: boolean
- fn.showExample: {}
  ->:
    - Ok_:
        link: fn.compute
- errors.RateLimit:
    - ErrorTooManyRequests: {}
- headers.Identity:
    "@user": string
  ->: {}
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
