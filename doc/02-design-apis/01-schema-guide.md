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
JSON collection types. In checked-in YAML examples, scalar type expressions stay
quoted so they continue to look like JSON values. When using JSON objects in
type expressions, the only allowed key type is `"string"`.

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
    field: "boolean"
    anotherField: ["string"]
- struct.ExampleStruct2:
    optionalField!: "boolean"
    anotherOptionalField!: "integer"
```

#### As a type expression

A struct definition itself can be used as a type reference.

| Type Expression             | Example allowed JSON values                           | Example disallowed JSON values     |
| --------------------------- | ----------------------------------------------------- | ---------------------------------- |
| `"struct.ExampleStruct1"`   | `{"field": true, "anotherField": ["text1", "text2"]}` | `null`, `{}`                       |
| `"struct.ExampleStruct2"`   | `{"optionalField!": true}`, `{}`                      | `null`, `{"wrongField": true}`     |
| `["struct.ExampleStruct2"]` | `[{"optionalField!": true}]`                          | `[null]`, `[{"wrongField": true}]`, `[{"optionalField": true}]` |

> [!IMPORTANT]
> Optionality is encoded in the field key itself, both in the schema and on
> the wire. Note that in the above example `{"optionalField": true}` is invalid;
> it must be `[{"optionalField!": true}]`

### Union

Type expressions can be encased in a tagged structured object (sum type). Unions
may be used in any type expression.

At least one tag is required.

```yaml
- union.ExampleUnion1:
    - Tag:
        field: "integer"
    - EmptyTag: {}
- union.ExampleUnion2:
    - Tag:
        optionalField!: "string"
```

#### As a type expression

A union definition itself can be used a type reference.

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

```yaml
- fn.exampleFunction1:
    field: "integer"
    optionalField!: "string"
  ->:
    - Ok_:
        field: "boolean"
- fn.exampleFunction2: {}
  ->:
    - Ok_: {}
    - Error:
        field: "string"
```

| Example Request                               | Example Response                     |
| --------------------------------------------- | ------------------------------------ |
| `[{}, {"fn.exampleFunction1": {"field": 1}}]` | `[{}, {"Ok_": {"field": true}}]`     |
| `[{}, {"fn.exampleFunction2": {}}]`           | `[{}, {"Error": {"field": "text"}}]` |

#### As a type expression

A function definition itself can be used as a type reference in order to
approximate "links" across the API interface, which take the form of a
prepopulated function call.

Note that when referenced as a type in type expressions, the result union is unused.

Functions cannot be used in type expressions that extend down from a top-level
function argument.

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
        field: "integer"
    - Error2: {}
```

For example, if placed in the same schema, the above error definition would
apply the errors `Error1` and `Error2` to both the `fn.exampleFunction1` and
`fn.exampleFunction2` functions from the previous section, as indicated below
(Note, the following example only illustrates the effect of the errors
definition at schema load time; the original schema is not re-written.)

```yaml
- fn.exampleFunction1:
    field: "integer"
    optionalField!: "string"
  ->:
    - Ok_:
        field: "boolean"
    - Error1:
        field: "integer"
    - Error2: {}
- fn.exampleFunction2: {}
  ->:
    - Ok_: {}
    - Error:
        field: "string"
    - Error1:
        field: "integer"
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
        result: "string"
```

✅ Good:
```yaml
- fn.exampleFunction: {}
  ->:
    - Ok_:
        result!: "string"
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
    "@requestHeader": "boolean"
    "@anotherRequestHeader": "integer"
  ->:
    "@responseHeader": "string"
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
    field: "boolean"
- struct.ExampleUnion:
    - ///: The default `Tag` that contains a `field`.
      Tag:
        field: "integer"
```

#### Multi-line

```yaml
- ///: |
    A struct that contains a field.

    Fields:
      - `field` (type: `boolean`)
  struct.ExampleStruct:
    field: "boolean"
```

## Automatic Definitions

Some definitions are automatically appended to your schema at runtime.

### Standard Definitions

Standard definitions include utility functions, like `fn.ping_`, and common
errors, like `ErrorInvalidRequest` and `ErrorUnknown_`. These are always
included and cannot be turned off.

`ErrorUnknown_` stays intentionally generic on the wire, but it includes a
`caseId`. Server implementations should log that `caseId` alongside the real
error so operators can match a client-reported `caseId` back to the
corresponding server-side stack trace or log entry.

The `fn.api_` helper returns the user-facing schema by default. Pass
`{"includeInternal!": true}` to include these standard Telepact definitions in
the response. Pass `{"includeExamples!": true}` to attach deterministic example
payloads to each returned schema entry. For mock servers, the expanded response
also includes the bundled mock schema definitions.

You can find all standard definitions
[here](../../common/internal.telepact.yaml).

### Auth Definitions

Auth definitions include the `@auth_` header and the `ErrorUnauthenticated_` and
`ErrorUnauthorized_` errors. These are included conditionally if the API writer
defines a `union.Auth_` definition in their schema, because the auth header
definition data type references it, as in `"@auth_": "union.Auth_"`.

The canonical Telepact auth contract is to place client-visible credential
variants in `union.Auth_` and carry them in `@auth_`. API writers are strongly
encouraged to reuse that shape rather than inventing a separate public auth
header, because `@auth_` is treated with greater sensitivity throughout the
Telepact ecosystem.

You can find details about auth definitions
[here](../../common/auth.telepact.yaml).
For the full Telepact auth model, including transport extraction and
server normalization, see the [Auth Guide](../03-build-clients-and-servers/05-auth.md).

### Mock Definitions

Mock definitions include mocking functions, like `fn.createStub_` and
`fn.verify_` for use in tests. These definitions are included if the API is
served with a `MockServer` rather than a `Server` in the Telepact server-side
library.

These schemas also include reserved `_ext.*_` extension types. Unlike ordinary
schema definitions, extension types are placeholders whose actual validation
rules come from Telepact runtime behavior and surrounding schema context.

You can find all mock definitions
[here](../../common/mock-internal.telepact.yaml).
There is also an overview of Telepact extension types [here](./03-extensions.md)
and a mock-specific extension guide [here](./05-mock-extensions.md).

## Full Example

### Schema

```yaml
- ///: A calculator app that provides basic math computation capabilities.
  info.Calculator: {}
- ///: A function that adds two numbers.
  fn.add:
    x: "number"
    y: "number"
  ->:
    - Ok_:
        result: "number"
- ///: |
    Save a variable with a given `name` and `value`. If a variable with the same name already exists, it will be overwritten.
  fn.saveVariable:
    name: "string"
    value: "number"
  ->:
    - Ok_: {}
- ///: A mathematical variable represented by a `name` that holds a certain `value`.
  struct.Variable:
    name: "string"
    value: "number"
- ///: |
    Save a map of `variables` where keys are variable names and values are their corresponding numeric values. Existing variables with the same names will be overwritten.
  fn.saveVariables:
    variables: {"string": "number"}
  ->:
    - Ok_: {}
- ///: |
    Retrieve a variable by its `name`.
  fn.getVariable:
    name: "string"
  ->:
    - Ok_:
        variable!: "struct.Variable"
- ///: |
    Retrieve all variables.
  fn.getVariables: {}
  ->:
    - Ok_:
        variables: ["struct.Variable"]
- ///: |
    Delete a variable by its `name`.
  fn.deleteVariable:
    name: "string"
  ->:
    - Ok_: {}
- ///: |
    Delete multiple variables by their `names`.
  fn.deleteVariables:
    names: ["string"]
  ->:
    - Ok_: {}
- ///: |
    Evaluate an `expression` and return the result.
  fn.evaluate:
    expression: "union.Expression"
  ->:
    - Ok_:
        result: "number"
        saveResult: "fn.saveVariable"
    - ErrorUnknownVariables:
        unknownVariables: ["string"]
    - ErrorCannotDivideByZero: {}
- ///: |
    A mathematical expression, either a `Constant`, a `Variable`, or a binary operation (`Add`, `Sub`, `Mul`, `Div`).
  union.Expression:
    - ///: A constant numeric `value`.
      Constant:
        value: "number"
    - ///: A variable reference by `name`.
      Variable:
        name: "string"
    - ///: An addition expression, `left` plus `right`.
      Add:
        left: "union.Expression"
        right: "union.Expression"
    - ///: A subtraction expression, `left` minus `right`.
      Sub:
        left: "union.Expression"
        right: "union.Expression"
    - ///: A multiplication expression, `left` times `right`.
      Mul:
        left: "union.Expression"
        right: "union.Expression"
    - ///: A division expression, `left` divided by `right`.
      Div:
        left: "union.Expression"
        right: "union.Expression"
- ///: |
    Get previous computations, ordered from most recent to least recent, up to the specified `limit`.
  fn.getPaperTape:
    limit!: "integer"
  ->:
    - Ok_:
        tape: ["struct.Evaluation"]
- ///: |
    A record of an evaluated expression, including the original `expression`, the computed `result`, the `timestamp` of evaluation, and whether the evaluation was `successful`.
  struct.Evaluation:
    expression: "union.Expression"
    result: "number"
    timestamp: "integer"
    successful: "boolean"
- ///: |
    Claim a session for the given `username`, if available.
  fn.login:
    username: "string"
  ->:
    - Ok_:
        token: "string"
    - ErrorUsernameAlreadyInUse: {}
- ///: |
    End the session for the given `username`, and delete all information related to it. Requires session authentication for the given `username`.
  fn.logout:
    username: "string"
  ->:
    - Ok_: {}
- union.Auth_:
    - Ephemeral:
        username: "string"
    - Session:
        token: "string"
```

### Valid Client/Server Interactions

```
-> [{}, {"fn.ping_": {}}]
<- [{}, {"Ok_": {}}]

-> [{}, {"fn.add": {"x": 1, "z": 2}}]
<- [{}, {"ErrorInvalidRequestBody_": {"cases": [{"path": ["fn.add", "z"], "reason": {"ObjectKeyDisallowed": {}}}, {"path": ["fn.add"], "reason": {"RequiredObjectKeyMissing": {"key": "y"}}}]}}]

-> [{}, {"fn.add": {"x": 1, "y": 2}}]
<- [{}, {"Ok_": {"result": 3}}]

-> [{}, {"fn.login": {"username": "bob"}}]
<- [{}, {"Ok_": {"token": "token-bob"}}]

-> [{"@auth_": {"Ephemeral": {"username": "bob"}}}, {"fn.saveVariables": {"variables": {"a": 1, "b": 2}}}]
<- [{}, {"Ok_": {}}]

-> [{"@auth_": {"Session": {"token": "token-bob"}}}, {"fn.evaluate": {"expression": {"Mul": {"left": {"Constant": {"value": 5}}, "right": {"Variable": {"name": "b"}}}}}}]
<- [{}, {"Ok_": {"result": 10, "saveResult": {"fn.saveVariable": {"name": "result", "value": 10}}}}]

-> [{"@auth_": {"Session": {"token": "token-bob"}}}, {"fn.evaluate": {"expression": {"Div": {"left": {"Variable": {"name": "a"}}, "right": {"Constant": {"value": 0}}}}}}]
<- [{}, {"ErrorCannotDivideByZero": {}}]

-> [{"@auth_": {"Ephemeral": {"username": "bob"}}}, {"fn.evaluate": {"expression": {"Add": {"left": {"Variable": {"name": "a"}}, "right": {"Variable": {"name": "missing"}}}}}}]
<- [{}, {"ErrorUnknownVariables": {"unknownVariables": ["missing"]}}]

-> [{"@auth_": {"Ephemeral": {"username": "bob"}}}, {"fn.getPaperTape": {"limit!": 2}}]
<- [{}, {"Ok_": {"tape": [{"expression": {"Add": {"left": {"Variable": {"name": "a"}}, "right": {"Variable": {"name": "missing"}}}}, "result": 0, "timestamp": 1710000001, "successful": false}, {"expression": {"Mul": {"left": {"Constant": {"value": 5}}, "right": {"Variable": {"name": "b"}}}}, "result": 10, "timestamp": 1710000000, "successful": true}]}}]

-> [{"@auth_": {"Ephemeral": {"username": "bob"}}}, {"fn.getVariables": {}}]
<- [{}, {"Ok_": {"variables": [{"name": "a", "value": 1}, {"name": "b", "value": 2}]}}]

-> [{"@auth_": {"Session": {"token": "token-bob"}}}, {"fn.logout": {"username": "bob"}}]
<- [{}, {"Ok_": {}}]
```
