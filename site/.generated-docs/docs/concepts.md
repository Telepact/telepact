# Concepts

## Quickstart

The minimum Telepact API ecosystem is established by a server defining a
Telepact API schema, and serving it using one of the Telepact libraries.

Specify your API:

```sh
$ cat ./api/math.telepact.yaml
```

```yaml
- ///: Divide two integers, `x` and `y`.
  fn.divide:
    x: "integer"
    y: "integer"
  ->:
    - Ok_:
        result: "number"
    - ErrorCannotDivideByZero: {}
```

Serve it with one of the Telepact libraries over a transport of your choice.
For more concrete HTTP and WebSocket patterns, see the
[Transport Guide](#transport-guide).

```sh
$ cat ./server.py
```

```py
from telepact import FunctionRouter, TelepactSchema, Server, Message
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
import uvicorn

async def divide(function_name, request_message):
    arguments = request_message.body[function_name]
    x = arguments['x']
    y = arguments['y']
    if y == 0:
        return Message({}, {'ErrorCannotDivideByZero': {}})

    result = x / y
    return Message({}, {'Ok_': {'result': result}})

options = Server.Options()

api = TelepactSchema.from_directory('./api')
function_router = FunctionRouter()
function_router.register_unauthenticated_routes({'fn.divide': divide})
server = Server(api, function_router, options)

async def http_handler(request):
    request_bytes = await request.body()
    response = await server.process(request_bytes)
    response_bytes = response.bytes
    media_type = 'application/octet-stream' if '@bin_' in response.headers else 'application/json'
    return Response(content=response_bytes, media_type=media_type)

routes = [
    Route('/api/telepact', endpoint=http_handler, methods=['POST']),
]

app = Starlette(routes=routes)

uvicorn.run(app, host='0.0.0.0', port=8000)
```

```sh
$ uv add uvicorn starlette telepact
$ uv run python ./server.py
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

### Next steps

- [Transport Guide](#transport-guide) for browser + Node HTTP and WebSocket patterns
- [Client Paths](#client-paths) for choosing between plain JSON, runtime libraries, and generated code
- [Auth Guide](#auth-guide) when the API needs caller identity
- [Tooling Workflow](#tooling-workflow) for `fetch`, `compare`, `mock`, and `codegen`
- [Operating Boundary Guide](#operating-boundary-guide) for Telepact-specific compatibility and observability boundaries
- [Demos](examples.md) for runnable end-to-end examples
- [Docs home](index.md) for the rest of the documentation map

## Schema Writing Guide

This guide explains how to understand and write Telepact schema files.

For normal checked-in authoring, prefer `*.telepact.yaml`. YAML is easier to
read at rest, especially for multi-line `///` docstrings. `*.telepact.json` is
still valid and remains the canonical lowered and wire-aligned representation.

The schema itself is still JSON-shaped. In this guide, checked-in schema-file
examples use YAML, while exact type-expression fragments and wire examples may
still use JSON syntax where that is more precise.

### Schema Directories

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

### Type Expression

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

#### Nullability

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

### Definitions

A Telepact Schema is an array of the following definition patterns:

-   struct
-   union
-   function
-   errors
-   headers

#### Struct Definition

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

##### As a type expression

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

#### Union

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

##### As a type expression

A union definition itself can be used a type reference.

| Type Expression         | Example allowed JSON values                          | Example disallowed JSON values                |
| ----------------------- | ---------------------------------------------------- | --------------------------------------------- |
| `"union.ExampleUnion1"` | `{"Tag": {"field": 0}}`, `{"EmptyTag": {}}`          | `null`, `{}`, `{"Tag": {"wrongField": true}}` |
| `"union.ExampleUnion2"` | `{"Tag": {"optionalField!": "text"}}`, `{"Tag": {}}` | `null`, `{}`                                  |

#### Function

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

##### As a type expression

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

#### Errors

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

##### Don't over-error

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

#### Headers

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

#### Docstrings

All top-level definitions and union tags (including errors and function results)
can include a docstring. Docstrings support markdown when rendered in the
Telepact console.

##### Single-line

```yaml
- ///: A struct that contains a `field`.
  struct.ExampleStruct:
    field: "boolean"
- union.ExampleUnion:
    - ///: The default `Tag` that contains a `field`.
      Tag:
        field: "integer"
```

##### Multi-line

```yaml
- ///: |
    A struct that contains a field.

    Fields:
      - `field` (type: `boolean`)
  struct.ExampleStruct:
    field: "boolean"
```

### Automatic Definitions

Some definitions are automatically appended to your schema at runtime.

#### Standard Definitions

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
[here](/common/internal.telepact.yaml).

#### Auth Definitions

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
[here](/common/auth.telepact.yaml).
For the full Telepact auth model, including transport extraction and
server normalization, see the [Auth Guide](#auth-guide).

#### Mock Definitions

Mock definitions include mocking functions, like `fn.createStub_` and
`fn.verify_` for use in tests. These definitions are included if the API is
served with a `MockServer` rather than a `Server` in the Telepact server-side
library.

These schemas also include reserved `_ext.*_` extension types. Unlike ordinary
schema definitions, extension types are placeholders whose actual validation
rules come from Telepact runtime behavior and surrounding schema context.

You can find all mock definitions
[here](/common/mock-internal.telepact.yaml).
There is also an overview of Telepact extension types [here](#extensions)
and a mock-specific extension guide [here](#mock-extensions).

### Full Example

#### Schema

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

#### Valid Client/Server Interactions

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

## Core Concepts

This page gives the shortest high-level map of Telepact's main ideas before you
dive into the detailed guides.

### Message shape

Telepact messages are always two JSON objects in an array:

```json
[headers, body]
```

- the first object holds headers
- the second object holds one request or response payload

Requests usually look like:

```json
[{}, {"fn.example": {"field": 1}}]
```

Responses usually look like:

```json
[{}, {"Ok_": {"field": 1}}]
```

For a more complete walkthrough, start with the
[Quickstart](#quickstart) or [Learn Telepact by Example](learn-by-example.md).

### Schema role

The Telepact schema is the contract that drives the whole ecosystem.

It defines:

- function arguments and results
- reusable structs and unions
- shared errors and headers
- what counts as valid requests and responses

That one schema also powers:

- server-side validation
- documentation rendering
- mock servers
- optional client code generation
- compatibility checks

For the full language, see the [Schema Writing Guide](#schema-writing-guide).

### Headers versus body

The body contains the main request or response payload.

Headers are separate metadata that travel alongside that payload. They are where
Telepact puts cross-cutting concerns such as auth, request ids, binary
negotiation, and select directives.

As a rule of thumb:

- use the body for domain data and function arguments/results
- use headers for metadata and transport-adjacent control signals

For more detail, see:

- [Transport Guide](#transport-guide)
- [Operating Boundary Guide](#operating-boundary-guide)
- [FAQ](#faq)

### Function links

Telepact functions can appear as data types inside other payloads. That lets a
server return a pre-populated function call that a client can follow later.

This gives Telepact a hypermedia-like capability without requiring HTTP-specific
link formats.

See:

- [Learn by Example: Functions](learn-by-example.md#08-functions)
- [Demos](examples.md)

### Select

Telepact supports response shaping through the `@select_` header. Clients can
ask for fewer fields from a response graph without inventing a separate query
language.

See:

- [Learn by Example: Select](learn-by-example.md#12-select)
- [`_ext.Select_`](#ext-select)

### Binary

Telepact can negotiate a compact binary representation at runtime. This means a
client can keep a JSON-first development workflow and still upgrade to binary
when it wants more efficiency.

See:

- [Learn by Example: Binary](learn-by-example.md#13-binary)
- [Learn by Example: Automatic binary negotiation](learn-by-example.md#20-automatic-binary-negotiation)

### Where to go next

- If you are designing an API, go to the [Schema Writing Guide](#schema-writing-guide).
- If you are building a client, go to [Client Paths](#client-paths).
- If you are building a server, go to [Server Paths](#server-paths).
- If you want the CLI and related workflows, go to [Tooling Workflow](#tooling-workflow).

## Extensions

Telepact reserves `_ext.*_` names for internal extension types. These are not
normal schema definitions for API authors to invent freely; they are built-in
placeholders that Telepact libraries interpret with custom validation and
example-generation logic.

### Why Extensions Exist

Normal Telepact definitions are self-describing:

- `struct.*` says exactly which fields are valid.
- `union.*` says exactly which tags and payloads are valid.
- `fn.*` says exactly which argument and result payloads are valid.

Extension types exist for the cases where that is not enough. Their valid JSON
shape depends on surrounding schema context rather than only on the definition
body itself.

That is why internal schemas define these types as empty objects like:

```yaml
_ext.Select_: {}
```

That does not mean "any empty object". It means "Telepact runtime provides the
real validation rules for this reserved type name".

### How Extensions Deviate From Normal Patterns

- Their definitions are placeholders, not full declarative schemas.
- Their valid shape is derived from nearby schema content or the active
  function, not only from the `_ext.*_` entry itself.
- They are implemented by Telepact libraries directly.
- They are intended for internal and mock-control workflows, not as a general
  schema authoring pattern.

If you need ordinary API data modeling, use `struct.*`, `union.*`, `fn.*`,
`headers.*`, and `errors.*`.

### Discovering Them

Call `fn.api_` with `{"includeInternal!": true}` to include internal schemas,
including `_ext.*_` definitions. Add `{"includeExamples!": true}` to get
deterministic example payloads for those types.

### Extension Guides

- [`_ext.Select_`](#ext-select) covers the `@select_` header and
  response-shaping payloads.
- [Mock extensions](#mock-extensions) covers `_ext.Call_`,
  `_ext.Stub_`, and how `fn.verify_` consumes `_ext.Call_`.

### Practical Guidance

- Prefer ordinary Telepact definitions unless you are intentionally integrating
  with Telepact internal or mock schemas.
- Treat `_ext.*_` types as reserved names with runtime-defined behavior.
- When in doubt, inspect `fn.api_` with internal definitions and examples
  enabled to see the exact shape the current schema exposes.

## ext.Select

`_ext.Select_` is the type behind the `@select_` header and any payload field
that wants the same "select fields from a result graph" behavior.

### Why It Is An Extension

The allowed shape is derived from the active function's `Ok_` result payload and
the nested structs and unions reachable from that result. That makes it
context-sensitive in a way that a single static `struct.*` definition cannot
express.

### Shape

`_ext.Select_` is always an object. Its keys are selection targets:

- `->` means "the active function result union".
- `struct.SomeType` means a reachable struct type.
- `union.SomeType` means a reachable union type.

Struct targets map to arrays of allowed field names:

```json
{
  "struct.Profile": ["displayName", "avatarUrl"]
}
```

Union targets map tag names to arrays of allowed field names for that tag:

```json
{
  "union.SearchResult": {
    "User": ["profile"],
    "Team": ["name"]
  }
}
```

The active result union can be selected through `->`:

```json
{
  "->": {
    "Ok_": ["profile", "summary"]
  },
  "struct.Profile": ["displayName"]
}
```

### How To Use It

- Send it in the `@select_` header to trim fields from response payloads.
- You only need to specify the parts you want to narrow; omitted selections
  default to the full reachable shape.
- It applies recursively through arrays and objects when the nested value type
  is a selected struct or union.
- It does not let you omit function argument fields. Selection is for response
  graphs, not for changing request-link shapes.

### End-To-End Example

Suppose the schema contains:

```yaml
- struct.ResultCard:
    title: string
    done!: boolean
- union.ResultItem:
    - Card:
        title: string
    - Note:
        body: string
- fn.selectNested: {}
  ->:
    - Ok_:
        card: struct.ResultCard
        item: union.ResultItem
```

If the server implementation would normally return:

```json
[
  {},
  {
    "Ok_": {
      "card": {
        "title": "Ship docs",
        "done!": false
      },
      "item": {
        "Card": {
          "title": "Ship docs"
        }
      }
    }
  }
]
```

then this request:

```json
[
  {
    "@select_": {
      "->": {
        "Ok_": ["card", "item"]
      },
      "struct.ResultCard": ["title"],
      "union.ResultItem": {
        "Card": []
      }
    }
  },
  {
    "fn.selectNested": {}
  }
]
```

changes the response shape to:

```json
[
  {},
  {
    "Ok_": {
      "card": {
        "title": "Ship docs"
      },
      "item": {
        "Card": {}
      }
    }
  }
]
```

The data values did not change. Only the reachable fields selected by the
header remained in the encoded response.

For a runnable minimal version of this pattern, see
[`example/py-select`](examples/py-select.md).

## Mock Extensions

This guide covers Telepact's mock-specific extension types: `_ext.Call_` and
`_ext.Stub_`.

### `_ext.Call_`

`_ext.Call_` represents one call made to a mocked non-internal function.

#### Why It Is An Extension

The top-level key must be one concrete function name from the mocked schema, and
the value must validate against that specific function's argument struct. That
is a "choose one key, then switch schema based on that key" rule derived from
the mocked API, not a fixed static union written inline once.

#### Shape

```json
{
  "fn.getUser": {
    "id": "user-1"
  }
}
```

Only non-internal mocked functions are valid. Mock control functions such as
`fn.createStub_` are not valid `_ext.Call_` payloads.

#### How To Use It

- Pass it to `fn.verify_` to assert that a matching call happened.
- Read it back from verification failures like `allCalls` or
  `additionalUnverifiedCalls`.
- The matching behavior such as strict versus partial matching is controlled by
  the mock API function that consumes the call, not by `_ext.Call_` itself.

#### End-To-End Example

Suppose the mocked API contains:

```yaml
- struct.User:
    id: string
    name: string
    admin!: boolean
- fn.getUser:
    id: string
    expand!: boolean
  ->:
    - Ok_:
        user: struct.User
```

Then `_ext.Call_` values look like:

```json
{
  "fn.getUser": {
    "id": "user-1"
  }
}
```

or:

```json
{
  "fn.getUser": {
    "id": "user-1",
    "expand!": true
  }
}
```

You send one of those objects to `fn.verify_`, and Telepact validates the inner
payload against the argument schema for the specific function key you chose.

### `_ext.Stub_`

`_ext.Stub_` represents a mock stub: a call matcher plus the result the mock
server should return.

#### Why It Is An Extension

It combines two schema-dependent pieces:

- one concrete non-internal `fn.*` argument payload
- the matching `->` result payload for that same function

That cross-links two dynamic choices from the mocked schema, so it is also not a
single closed `struct.*` definition.

#### Shape

```json
{
  "fn.getUser": {
    "id": "user-1"
  },
  "->": {
    "Ok_": {
      "name": "Ada"
    }
  }
}
```

#### How To Use It

- Pass it to `fn.createStub_` to install a stub on a mock server.
- The `fn.*` part is the matcher.
- The `->` part must be a valid result payload for that same function.
- Stub lifetime and matching behavior such as `strictMatch!` and `count!` are
  configured on `fn.createStub_`, not inside `_ext.Stub_`.

#### End-To-End Example

Using the same mocked `fn.getUser` schema as above, create a stub with:

```json
[
  {},
  {
    "fn.createStub_": {
      "stub": {
        "fn.getUser": {
          "id": "user-1"
        },
        "->": {
          "Ok_": {
            "user": {
              "id": "user-1",
              "name": "Ada"
            }
          }
        }
      }
    }
  }
]
```

The control call succeeds immediately:

```json
[
  {},
  {
    "Ok_": {}
  }
]
```

After that, the mock changes behavior for matching API calls. This request:

```json
[
  {},
  {
    "fn.getUser": {
      "id": "user-1",
      "expand!": true
    }
  }
]
```

returns:

```json
[
  {},
  {
    "Ok_": {
      "user": {
        "id": "user-1",
        "name": "Ada"
      }
    }
  }
]
```

because `fn.createStub_` defaults to partial argument matching. The extra
`expand!` field does not prevent the stub from matching.

A non-matching call still behaves like an unstubbed mock call:

```json
[
  {},
  {
    "fn.getUser": {
      "id": "user-2"
    }
  }
]
```

```json
[
  {},
  {
    "ErrorNoMatchingStub_": {}
  }
]
```

If you need exact argument equality instead, set `strictMatch!` to `true` on
`fn.createStub_`.

### `fn.verify_` With `_ext.Call_`

`fn.verify_` consumes an `_ext.Call_`, not an ordinary free-form object. The
chosen function name determines which argument schema Telepact validates
against, and the call shape you pass affects whether verification succeeds.

Continuing the previous example, suppose the mock has already recorded these two
calls:

```json
[
  {
    "fn.getUser": {
      "id": "user-1",
      "expand!": true
    }
  },
  {
    "fn.getUser": {
      "id": "user-2"
    }
  }
]
```

This verification request succeeds:

```json
[
  {},
  {
    "fn.verify_": {
      "call": {
        "fn.getUser": {
          "id": "user-1"
        }
      }
    }
  }
]
```

```json
[
  {},
  {
    "Ok_": {}
  }
]
```

because verification defaults to partial matching and `count!` defaults to
`{"AtLeast": {"times": 1}}`.

The same logical function can fail if you change the verification call:

```json
[
  {},
  {
    "fn.verify_": {
      "call": {
        "fn.getUser": {
          "id": "user-1"
        }
      },
      "strictMatch!": true
    }
  }
]
```

```json
[
  {},
  {
    "ErrorVerificationFailure": {
      "reason": {
        "TooFewMatchingCalls": {
          "wanted": {
            "AtLeast": {
              "times": 1
            }
          },
          "found": 0,
          "allCalls": [
            {
              "fn.getUser": {
                "id": "user-1",
                "expand!": true
              }
            },
            {
              "fn.getUser": {
                "id": "user-2"
              }
            }
          ]
        }
      }
    }
  }
]
```

because exact matching now requires the recorded argument to equal the given
argument exactly.

Changing only `count!` can also change the result:

```json
[
  {},
  {
    "fn.verify_": {
      "call": {
        "fn.getUser": {}
      },
      "count!": {
        "AtMost": {
          "times": 1
        }
      }
    }
  }
]
```

```json
[
  {},
  {
    "ErrorVerificationFailure": {
      "reason": {
        "TooManyMatchingCalls": {
          "wanted": {
            "AtMost": {
              "times": 1
            }
          },
          "found": 2,
          "allCalls": [
            {
              "fn.getUser": {
                "id": "user-1",
                "expand!": true
              }
            },
            {
              "fn.getUser": {
                "id": "user-2"
              }
            }
          ]
        }
      }
    }
  }
]
```

because the empty argument object partially matches both recorded `fn.getUser`
calls.

## Transport Guide

Telepact is transport-agnostic by design.

That means the Telepact libraries own message validation, schema semantics,
request and response serialization, binary negotiation, and related ecosystem
features, while your application owns the transport boundary that moves bytes in
and out.

In practice, the transport boundary is usually quite small:

- server code receives request bytes from a transport
- the Telepact server turns those bytes into a validated response message
- server code sends the response bytes back over the transport
- client code serializes a Telepact message into request bytes
- the transport sends those bytes to the remote service
- client code deserializes the response bytes back into a Telepact message

This guide shows concrete examples for two common transports:

- HTTP
- WebSockets

Runnable counterparts live under [`example/`](examples.md), including
[`example/py-links`](examples/py-links.md),
[`example/py-http-cookie-auth`](examples/py-http-cookie-auth.md), and
[`example/py-websocket`](examples/py-websocket.md).

The same pattern applies to NATS, stdio, queues, custom RPC layers, and other
IPC boundaries.

### The Core Cutpoint

The most important integration point is the raw byte boundary.

On the server side, the transport usually ends up calling:

```py
response = await server.process(request_bytes)
response_bytes = response.bytes
```

On the client side, the transport usually sits inside a Telepact adapter:

```py
async def adapter(message: Message, serializer: Serializer) -> Message:
    request_bytes = serializer.serialize(message)
    response_bytes = await transport.send(request_bytes)
    return serializer.deserialize(response_bytes)
```


### Example API

The examples below use this schema:

```yaml
- fn.greet:
    subject: string
  ->:
    Ok_:
      message: string
```

### HTTP

HTTP is the most common Telepact deployment shape. A typical setup is:

- one POST endpoint for Telepact requests
- request body contains Telepact request bytes
- response body contains Telepact response bytes
- `Content-Type` reflects whether the response is JSON or binary
- ordinary HTTP middleware can still sit around the Telepact core when needed

#### HTTP server example (Python + Starlette)

```py
from telepact import FunctionRouter, Message, Server, TelepactSchema
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
import uvicorn

schema = TelepactSchema.from_directory('./api')

async def greet(function_name: str, request_message: Message) -> Message:
    arguments = request_message.body[function_name]
    subject = arguments['subject']
    return Message({}, {'Ok_': {'message': f'Hello {subject}!'}})

options = Server.Options()
function_router = FunctionRouter()
function_router.register_unauthenticated_routes({'fn.greet': greet})
server = Server(schema, function_router, options)

async def http_handler(request):
    request_bytes = await request.body()

    # The transport cutpoint is tiny and explicit.
    response = await server.process(request_bytes)
    response_bytes = response.bytes

    media_type = (
        'application/octet-stream'
        if '@bin_' in response.headers
        else 'application/json'
    )
    return Response(content=response_bytes, media_type=media_type)

app = Starlette(routes=[
    Route('/api/telepact', endpoint=http_handler, methods=['POST']),
])

uvicorn.run(app, host='0.0.0.0', port=8000)
```

#### HTTP client example (browser TypeScript + fetch)

```ts
import { Client, ClientOptions, Message, Serializer } from 'telepact';

const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
  const requestBytes = serializer.serialize(message);

  const response = await fetch('http://localhost:8000/api/telepact', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: requestBytes,
  });

  const responseBytes = new Uint8Array(await response.arrayBuffer());
  return serializer.deserialize(responseBytes);
};

const client = new Client(adapter, new ClientOptions());

const response = await client.request(
  new Message({}, { 'fn.greet': { subject: 'World' } }),
);

if (response.getBodyTarget() === 'Ok_') {
  console.log(response.getBodyPayload().message);
}
```

#### HTTP notes

- `fetch` accepts binary request bodies, so the same client can work with JSON
  or binary Telepact payloads.
- Reverse proxies and other HTTP concerns still remain possible around a
  Telepact endpoint when your application needs them.

### WebSockets

WebSockets work well when you want a long-lived connection but still want your
application to exchange discrete Telepact request and response messages.

A common pattern is one Telepact request per WebSocket message and one Telepact
response per WebSocket message.

#### WebSocket server example (Python + Starlette)

```py
from telepact import FunctionRouter, Message, Server, TelepactSchema
from starlette.applications import Starlette
from starlette.routing import WebSocketRoute
import uvicorn

schema = TelepactSchema.from_directory('./api')

async def greet(function_name: str, request_message: Message) -> Message:
    arguments = request_message.body[function_name]
    subject = arguments['subject']
    return Message({}, {'Ok_': {'message': f'Hello {subject}!'}})

options = Server.Options()
function_router = FunctionRouter()
function_router.register_unauthenticated_routes({'fn.greet': greet})
server = Server(schema, function_router, options)

async def websocket_handler(websocket):
    await websocket.accept()
    try:
        while True:
            request_bytes = await websocket.receive_bytes()
            response = await server.process(request_bytes)
            await websocket.send_bytes(response.bytes)
    except Exception:
        await websocket.close()

app = Starlette(routes=[
    WebSocketRoute('/ws/telepact', endpoint=websocket_handler),
])

uvicorn.run(app, host='0.0.0.0', port=8000)
```

#### WebSocket client example (browser TypeScript)

This example opens a new WebSocket per request to keep the example small.
Production clients will often reuse one socket and correlate in-flight requests
with an application-level request id in headers or payloads.

```ts
import { Client, ClientOptions, Message, Serializer } from 'telepact';

const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
  const requestBytes = serializer.serialize(message);

  const responseBytes = await new Promise<Uint8Array>((resolve, reject) => {
    const ws = new WebSocket('ws://localhost:8000/ws/telepact');
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => {
      ws.send(requestBytes);
    };

    ws.onmessage = (event) => {
      resolve(new Uint8Array(event.data as ArrayBuffer));
      ws.close();
    };

    ws.onerror = () => {
      reject(new Error('WebSocket transport failed'));
      ws.close();
    };
  });

  return serializer.deserialize(responseBytes);
};

const client = new Client(adapter, new ClientOptions());

const response = await client.request(
  new Message({}, { 'fn.greet': { subject: 'World' } }),
);

if (response.getBodyTarget() === 'Ok_') {
  console.log(response.getBodyPayload().message);
}
```

#### WebSocket notes

- Reusing a single socket is usually better than reconnecting per request.
- If you multiplex requests over one socket, add an explicit correlation id so
  responses can be matched to callers.
- The transport cutpoint is also a natural place for heartbeat handling,
  connection lifecycle metrics, auth refresh, and backpressure policy.

### See also

- [Quickstart](#quickstart)
- [FAQ](#faq)
- [Runtime Error Guide](#runtime-error-guide)

## Client Paths

Telepact clients can participate at different levels of sophistication. Start
with the lightest path that fits your needs, then upgrade only where it helps.

### Path 1: Plain JSON client

The lightest client needs only:

- a JSON library
- a transport library
- knowledge of the Telepact message format

This path works well when you want:

- quick experiments
- shell scripts or browser fetch code
- a language that does not yet have a Telepact library
- the lowest possible tooling burden

Start here:

- [Quickstart](#quickstart)
- [Core Concepts](#core-concepts)
- [Transport Guide](#transport-guide)

### Path 2: Telepact client library

Use a Telepact client library when you want help with message construction,
serialization, validation-aware workflows, and binary negotiation.

This is the best default path when you want more than raw JSON but do not want
to commit to generated bindings yet. Pair it with a Telepact mock when you want
schema-backed confidence that your integration will succeed before you point at
the live server.

Available library docs:

- [TypeScript](lib-and-sdk-survey.md#typescript)
- [Python](lib-and-sdk-survey.md#python)
- [Java](lib-and-sdk-survey.md#java)
- [Go](lib-and-sdk-survey.md#go)

This path works well when you want:

- a supported runtime library
- easier request/response handling
- a clearer adapter boundary around your transport

### Path 3: Generated client code

Use generated code when you want the strongest typing and the most ergonomic
application-level API for your target language. This is an optional upgrade on
top of the runtime client path, not the recommended starting point.

This path works well when you want:

- compile-time feedback in supported languages
- stable generated bindings for a shared schema
- less hand-written request boilerplate
- an SDK-like API surface for humans, IDEs, and static analysis

Start here:

- [Learn by Example: Code generation](learn-by-example.md#21-code-generation)
- [Tooling Workflow](#tooling-workflow)
- [Telepact CLI](lib-and-sdk-survey.md#cli)

### Choosing between them

Use plain JSON when simplicity matters most.

Use a library when you want the Telepact runtime to handle more of the protocol
details for you.

Use a mock when you want to validate real requests against the schema, generate
schema-valid responses, and verify expected calls during integration work.

Use generated code when you want the most type-safe and ergonomic application
integration on top of a supported language runtime.

These paths are complementary rather than exclusive. Many teams start with
plain JSON or a library, use a mock for schema-backed confidence, then add
generated code only for the callers that benefit from stronger static
ergonomics.

## Server Paths

Every Telepact server follows the same basic shape:

1. define a schema directory
2. load that schema with a Telepact runtime
3. route validated requests to function handlers
4. connect the runtime to a transport boundary

### Choose a runtime

Telepact currently ships server libraries for:

- [TypeScript](lib-and-sdk-survey.md#typescript)
- [Python](lib-and-sdk-survey.md#python)
- [Java](lib-and-sdk-survey.md#java)
- [Go](lib-and-sdk-survey.md#go)

Pick the runtime that fits the service you are already building. Telepact is
transport-agnostic, so the same schema and server shape can sit behind HTTP,
WebSockets, or another IPC boundary that moves bytes.

### Minimal server path

If you want the fastest path to a running server:

- follow the [Quickstart](#quickstart)
- continue with [Learn by Example: Minimum server](learn-by-example.md#22-minimum-server)
- use the runtime README for your language

### Transport adapter path

Keep the transport adapter thin.

Its job is usually just:

- receive request bytes
- call `server.process(...)`
- send response bytes back through the transport

See the [Transport Guide](#transport-guide) for concrete HTTP and WebSocket
patterns.

### Middleware and auth path

Put request-level concerns near the Telepact runtime boundary:

- auth normalization
- request ids
- logging
- metrics
- other policy checks

Start here:

- [Auth Guide](#auth-guide)
- [Learn by Example: Auth](learn-by-example.md#18-auth)
- [Learn by Example: Server auth](learn-by-example.md#24-server-auth)
- [Learn by Example: Managed auth](learn-by-example.md#25-managed-auth)
- [Operating Boundary Guide](#operating-boundary-guide)

### Operating boundary path

When placing Telepact inside a larger service, focus on:

- schema compatibility policy
- where auth and observability hooks attach
- transport responsibilities versus Telepact responsibilities
- exact runtime/tool versioning

Start here:

- [Operating Boundary Guide](#operating-boundary-guide)
- [Runtime Error Guide](#runtime-error-guide)

## Auth Guide

This page describes Telepact's auth convention.

The canonical model is:

1. define every client-visible credential shape in `union.Auth_`
2. carry those credentials in `@auth_`
3. use the transport adapter to extract transport-specific credentials into `@auth_` when needed
4. use `onAuth` to validate `@auth_` and normalize it into internal request headers such as `@userId`, `@tenantId`, or `@scopes`
5. enforce authorization in middleware and function routes
6. return `ErrorUnauthenticated_` or `ErrorUnauthorized_` for auth failures

This keeps Telepact's auth surface small and explicit while leaving credential
issuance, cookie policy, token minting, and gateway behavior to the surrounding
service.

### What Telepact owns vs what your service owns

Telepact owns:

- the schema shape for `union.Auth_`
- the conventional `@auth_` request header
- the standard `ErrorUnauthenticated_` and `ErrorUnauthorized_` error shapes
- validation of schema-defined auth payloads
- the `onAuth` hook and middleware path where normalized request headers can be attached

Your surrounding service owns:

- how credentials arrive over HTTP, WebSockets, NATS, queues, or other transports
- bearer token verification, session lookup, API key lookup, mTLS identity extraction, and similar checks
- cookie issuance, cookie flags, CSRF protection, token refresh, logout, revocation, and secret management
- authorization policy decisions tied to business data and deployment-specific infrastructure

Telepact is transport-agnostic. It does not define HTTP auth middleware, cookie
settings, OAuth flows, or gateway behavior. It gives you one canonical in-band
message shape once credentials cross into the Telepact server boundary.

### Canonical schema shape

Define auth credentials in `union.Auth_`:

```yaml
- union.Auth_:
    - Session:
        token: string
    - Bearer:
        token: string
```

When `union.Auth_` exists, Telepact adds these standard definitions:

```yaml
- headers.Auth_:
    "@auth_": "union.Auth_"

- errors.Auth_:
    - ErrorUnauthenticated_:
        message!: string
    - ErrorUnauthorized_:
        message!: string
```

Schema rule of thumb:

- put client-visible credential variants in `union.Auth_`
- keep normalized identity headers such as `@userId` or `@tenantId` out of the public schema unless clients are meant to send or inspect them directly

`union.Auth_` is the canonical public auth contract. Avoid inventing a second
public auth header when `@auth_` already represents the caller credentials.

### `@auth_`

`@auth_` is the canonical place for credentials inside a Telepact request.

Two common ways it gets populated:

- a Telepact-aware client sends `@auth_` directly
- the transport adapter extracts credentials from transport-specific state and writes `@auth_` before calling `server.process(...)`

Telepact runs `onAuth` only for functions registered in the authenticated route
map. If a protected call is missing `@auth_`, Telepact returns
`ErrorUnauthenticated_` before it reaches your handler.

### Auth error shapes

Use the standard errors consistently:

- `ErrorUnauthenticated_`: credentials were missing, malformed, expired, revoked, or otherwise not accepted
- `ErrorUnauthorized_`: the caller was authenticated, but is not allowed to perform the requested action

That split keeps auth failures predictable across services and across language
implementations.

### Transport-layer credential extraction

Transport code should stay thin. Its auth job is only to translate transport
state into the canonical Telepact auth shape.

Examples:

- HTTP cookie -> `@auth_ = {"Session": {"token": ...}}`
- HTTP `Authorization: Bearer ...` -> `@auth_ = {"Bearer": {"token": ...}}`
- gateway-verified service credential -> `@auth_ = {"Bearer": {"token": ...}}` or another `union.Auth_` variant

The transport adapter should not grow its own business authorization model. Its
role is extraction and translation.

### Normalization inside the Telepact server

Inside the server:

1. `onAuth` receives headers, including `@auth_`
2. `onAuth` validates or resolves the credential
3. `onAuth` returns normalized internal headers
4. middleware and function routes use those normalized headers for policy and business logic

Convention:

- if `onAuth` returns normally, authentication succeeded and the returned headers are the normalized identity
- if credentials are invalid or the auth backend fails, throw from `onAuth` instead of returning empty or partial identity and checking later in shared middleware

That keeps the auth boundary attached to the authenticated route map and avoids
accidentally turning shared middleware into a gate for unauthenticated routes.

Define protected handlers in the authenticated route map and public handlers in
the unauthenticated route map. Telepact automatically keeps `fn.ping_` and
`fn.api_` unauthenticated.

Typical normalized headers are internal values like:

- `@userId`
- `@tenantId`
- `@role`
- `@scopes`

Keep these normalized headers service-specific. They are usually internal
server-to-handler data, not public client contract.

### Browser / session-cookie flow

For browser sessions:

1. the browser sends its session cookie over HTTP
2. the HTTP adapter reads the cookie
3. the adapter writes the canonical `@auth_` value
4. `onAuth` looks up the session and returns normalized identity headers
5. handlers authorize with those normalized headers

This is a common cookie pattern because the browser does not need to
handcraft `@auth_`, while the Telepact server still receives one canonical auth
shape internally.

See:

- [Learn by Example: Managed auth](learn-by-example.md#25-managed-auth)
- [`example/py-http-cookie-auth`](examples/py-http-cookie-auth.md)

### Service-to-service flow

For service-to-service calls, a common shape is explicit `@auth_` when the
caller is already constructing Telepact messages.

That usually means:

1. the calling service obtains a bearer token, API key, or other service credential
2. the caller sends it in `@auth_` using a `union.Auth_` variant
3. `onAuth` validates the credential and returns normalized internal headers
4. middleware and handlers authorize from the normalized identity

If an intermediary gateway or transport already owns the raw credential, it can
still translate that transport-specific credential into `@auth_` before the
Telepact server processes the request.

### In one sentence

Model caller credentials in `union.Auth_`, move them through `@auth_`, normalize
them with `onAuth`, authorize on normalized identity, and keep transport- and
deployment-specific auth mechanics outside Telepact itself.

## Tooling Workflow

Telepact's tooling is designed around the schema. The same contract that powers
runtime validation also powers fetching, comparison, mocking, code generation,
and interactive docs.

### Fetch a schema

Use the CLI to retrieve a schema from a running Telepact server and store it
locally.

This is useful when you want to:

- inspect a live API contract
- save a schema for local development
- feed the schema into other Telepact tools

See:

- [Telepact CLI](lib-and-sdk-survey.md#cli)

### Compare schema versions

Use `telepact compare` to check backwards compatibility between an old schema and
a new schema.

This is useful when you want to:

- gate schema changes in CI
- make compatibility an explicit release check

In practice, that often means comparing the checked-in schema directory on your
branch with the version from `origin/main` or the last release tag:

```sh
old_dir="$(mktemp -d)"
new_dir="$(mktemp -d)"

git archive origin/main api | tar -x -C "$old_dir"
git archive HEAD api | tar -x -C "$new_dir"

telepact compare \
  --old-schema-dir "$old_dir/api" \
  --new-schema-dir "$new_dir/api"
```

Replace `api` with the schema directory your service checks in.

See:

- [Operating Boundary Guide](#operating-boundary-guide)
- [Telepact CLI](lib-and-sdk-survey.md#cli)

### Mock an API

Use `telepact mock` when clients need to develop before a live server is ready
or when tests need schema-valid responses on demand.

This is useful when you want to:

- unblock client development
- test against schema-valid responses
- add stubs and verification around expected calls
- make mock-first integration validation your default workflow

For many integrations, this is the best default confidence path: point your
consumer at a Telepact mock first, let the mock validate the requests you
actually send, then switch to the live server later.

See:

- [Learn by Example: Mock server](learn-by-example.md#14-mock-server)
- [Learn by Example: Stock mock](learn-by-example.md#15-stock-mock)
- [Learn by Example: Stubs](learn-by-example.md#16-stubs)
- [Learn by Example: Verify](learn-by-example.md#17-verify)

### Generate code

Use `telepact codegen` to generate bindings from a schema.

This is useful when you want:

- stronger typing in supported languages
- generated request/response models
- less manual client boilerplate
- a more ergonomic static API than the runtime client alone

Code generation is optional. Start with plain JSON or a Telepact runtime
library, use the mock server for schema-backed validation, and add generated
bindings only when the extra static ergonomics are worth the toolchain cost.

See:

- [Learn by Example: Code generation](learn-by-example.md#21-code-generation)
- [Client Paths](#client-paths)
- [Telepact CLI](lib-and-sdk-survey.md#cli)

### Use the browser console

Use the [Telepact Console](lib-and-sdk-survey.md#console) when you want interactive
documentation, request drafting, and live requests against a running Telepact
server.

## Operating Boundary Guide

This page is intentionally narrow.

Telepact is a small RPC layer, not a production framework. It does not try to
teach general service operations or prescribe one enterprise rollout model. Its
job is to make the Telepact boundary explicit so your surrounding service can
attach its own auth, logging, metrics, routing, and deployment systems in the
right places.

For byte-level wiring, see the
[Transport Guide](#transport-guide).

### 1. What Telepact owns

Telepact owns:

- schema-defined request and response shapes
- schema validation
- serialization and deserialization
- binary negotiation
- request / response semantics such as `ErrorInvalid*` and `ErrorUnknown_`
- the middleware and hook points around a validated Telepact request

Telepact does **not** own:

- gateways, meshes, or reverse proxies
- TLS, sockets, and HTTP-specific policy
- service discovery or load balancing
- rate limiting, retries, or circuit breaking
- tracing backends, metrics backends, or log pipelines
- deployment policy, rollout procedure, or incident response process

That split is the main operating model. Keep the Telepact core small, then let
your service's own production stack handle the rest.

### 2. Where cross-cutting concerns belong

Use this placement guide:

| Concern | Primary home |
| --- | --- |
| TLS, sockets, HTTP / WebSocket details, request size limits, timeouts | Transport layer or infrastructure around Telepact |
| Service discovery, load balancing, retries, circuit breaking | Caller, gateway, mesh, or other surrounding infrastructure |
| Credentials crossing from HTTP cookies, bearer tokens, or other transport state into Telepact | Transport adapter |
| Auth normalization, request ids, per-function logs, per-function metrics | Telepact middleware and hooks |
| Domain authorization and business rules | Middleware and function routes that own the data |
| Schema validation, serialization, Telepact headers, Telepact errors | Telepact runtime |

Rule of thumb:

- if it depends on network or transport details, keep it outside Telepact
- if it depends on validated Telepact headers, function names, or Telepact
  outcomes, Telepact middleware is usually the right cutpoint
- if it depends on domain data or business rules, keep it with the handlers or
  surrounding service logic

### 3. Auth, logging, and metrics

Telepact cares mainly about placement.

#### Auth

Telepact's auth convention is:

- define caller-visible credential variants in `union.Auth_`
- carry them in `@auth_`
- translate transport-specific credential state into `@auth_` at the transport boundary when needed
- use `onAuth` to normalize authenticated identity into internal headers
- keep authorization decisions near the business logic that owns the resource

The Telepact-specific point is not how your organization should issue tokens or
run a gateway. It is that Telepact has one conventional in-band auth shape and
one conventional hook point once credentials cross into the Telepact request.

Use the standard auth errors consistently:

- `ErrorUnauthenticated_` for missing or invalid credentials
- `ErrorUnauthorized_` for authenticated callers who are not allowed to perform the action

For the canonical schema shape and examples, see the
[Auth Guide](#auth-guide).

#### Logging and metrics

If you want Telepact-aware logs or metrics, emit them from middleware or hooks
that can see:

- the Telepact function name
- normalized caller context
- the response outcome
- elapsed time

Transport logs still answer different questions from Telepact logs. Transport
logs describe connections and byte-level behavior; Telepact logs can describe
which Telepact function ran and how it completed.

One Telepact-specific pitfall: avoid dumping whole request or response `Message`
objects just because they are available. Even though `@auth_` is treated
carefully by Telepact, application payloads may still contain sensitive data.

#### Request ids and tracing

Telepact can carry correlation data in headers, but it does not define a tracing
policy. The important Telepact point is simply to keep the ids consistent across
the transport boundary and the Telepact middleware boundary so the same request
can be correlated in both places.

### 4. Expose unique transports to CLI tooling through a proxy

If your production service speaks Telepact over a transport such as NATS, stdio,
queues, or another internal RPC boundary, the CLI tooling still works best when
it can reach a normal HTTP Telepact endpoint.

In that setup, expose a small proxy specifically for tooling and operational
access:

- keep the real Telepact server on its native transport
- expose fixed HTTP routes that map to the internal transport destinations your
  tooling needs
- forward raw Telepact request and response bytes through the proxy instead of
  re-implementing Telepact semantics there
- let `telepact fetch`, `telepact mock --http-url`, and related tooling talk to
  the proxy's HTTP surface

That keeps the transport-specific production boundary explicit while still
making Telepact tooling usable from standard developer environments.

For a runnable example, see
[`example/full-stack-proxy`](examples/full-stack-proxy.md), which
shows a browser and HTTP-facing proxy forwarding Telepact bytes to an internal
NATS subject.

### 5. Compatibility and upgrades

Telepact provides `telepact compare` because schema compatibility is part of the
Telepact contract surface.

The Telepact-specific guidance is:

- treat checked-in schema as part of the released contract
- compare old and new schema when the contract changes
- keep generated bindings, schema files, and Telepact runtime versions aligned
- stage breaking changes so callers are not forced across incompatible message
  shapes all at once

For the practical Git-based workflow to compare the checked-in schema on your
branch with `origin/main` or a release tag, see
[Tooling Workflow: Compare schema versions](#compare-schema-versions).

Telepact does not prescribe the surrounding rollout procedure. Whether your
organization uses canaries, blue/green, staged regional rollout, or something
else is outside this library's scope.

### 6. Error boundary notes

Telepact keeps wire behavior and local diagnostics separate:

- schema-invalid messages return `ErrorInvalid*`
- unexpected handler or serialization failures return `ErrorUnknown_` on the wire
- local hooks and exceptions carry the details needed for debugging

That separation is intentional. It keeps the public RPC surface stable while
still giving the surrounding service a place to log or inspect failures.

See the [Runtime Error Guide](#runtime-error-guide) for the current local error
categories.

## Runtime Error Guide

Telepact keeps wire compatibility and local diagnostics separate.

- On the wire, server-side unexpected failures still become `ErrorUnknown_`.
- Locally, Telepact libraries now try to classify failures so application logs
  and caught exceptions say whether the problem came from parsing, validation,
  serialization, transport, or user server logic (middleware / function routes).

### Failure Categories

| Category | What it means | Typical local signal |
| --- | --- | --- |
| `parse` | The server could not decode the incoming request bytes into a Telepact message. | `telepact request parsing failed while decoding the incoming message` |
| `validation` | A message was decoded, but Telepact rejected headers or body data against the schema. | `telepact response validation failed ...` or `telepact response header validation failed ...` |
| `serialization` | Telepact could not serialize or deserialize a message at the library boundary. | `telepact serialization failed ...` or `telepact client serialization or deserialization failed` |
| `transport` | The client adapter timed out or failed while talking to the remote service. | `telepact client transport failed` or `telepact client transport timed out ...` |
| `handler` | User server middleware or function-route code threw while handling a valid request message. | `telepact handler failed while handling fn.someCall` |

### Server-Side Behavior

For server code:

- invalid requests still return schema-level errors such as
  `ErrorInvalidRequestBody_` and `ErrorInvalidRequestHeaders_`
- invalid handler responses still return
  `ErrorInvalidResponseBody_` or `ErrorInvalidResponseHeaders_`
- unexpected handler or serialization failures still return `ErrorUnknown_`

When that happens, treat the `caseId` in `ErrorUnknown_` as a correlation ID:
log it on the server next to the real exception details, then use it to match a
client-side error report back to the corresponding server-side log entry.

For example, a Python server can log the correlation ID in `on_error`:

```py
def on_error(error: TelepactError) -> None:
    log.exception('telepact error case_id=%s', error.case_id, exc_info=error)
```

For a fuller walkthrough, see
[Learn by example: Logging](learn-by-example.md#23-logging).

The main change is the local callback surface:

- `options.onError` receives contextual errors instead of raw implementation
  exceptions where practical
- response-validation failures are reported to `onError` before Telepact returns
  the corresponding invalid-response union on the wire

### Client-Side Behavior

For client code:

- adapter timeouts and transport failures are categorized as `transport`
- serializer failures before request send or while decoding a response are
  categorized as `serialization`
- the original cause remains attached where the language runtime supports it

### Language Notes

- TypeScript: `TelepactError` exposes `kind` and preserves `cause` when
  available.
- Python: `TelepactError` and `SerializationError` carry `kind`, `cause`, and
  `context` attributes.
- Java: `TelepactError#getKind()` and `SerializationError#getContext()` expose
  the broad diagnostic category.
- Go: public client errors use `TelepactError` with `errors.Is` / `errors.As`
  support via `Unwrap()`. Internal server callbacks receive wrapped `error`
  messages with the same category wording.

### Debugging Rule Of Thumb

1. If the wire response is `ErrorInvalid*`, fix the schema mismatch first.
2. If the wire response is `ErrorUnknown_`, capture the client-visible `caseId`
   and match it against the same `caseId` in server logs; the local Telepact
   error should usually tell you whether the root cause was middleware /
   function-route code or serialization.
3. If the client raised before any response arrived, check whether the local
   error is `transport` or `serialization`.

## FAQ

### Who exactly needs to use Telepact libraries?

Telepact boasts a flexible development environment for clients, who are
allowed to bring as much or as little Telepact tooling as they like, including
no tooling at all in favor of industry standard JSON and network libraries.

The server, however, MUST use a Telepact library to serve its Telepact API.
Doing so ensures a rich Telepact ecosystem for developers and clients,
including features such as automatic API retrieval for mocking, documentation
browsing using the console, request validation, opt-in binary, and response
field selection.

### Why have both optional and nullable fields?

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

### Why do optional fields keep the `!` symbol in the request/response payloads?

If a field is marked as optional in the schema, such as `"field!": "integer"`,
it will keep that `!` symbol on live payloads, such as `"field!": 42`.

This pattern serves two purposes (1) to keep the schema and live payloads as
similar as possible, and (2) to alert code writers of the optional edge case.
If a client encounters something like `response['field!']` in code, the `!`
immediately alerts the code reader that an `undefined`-like value might be
returned from the code expression.

### Why can't header fields use the `!` symbol?

Headers definitions resemble structs, but unlike ordinary structs, all headers
are already optional by default. As a result, header names never take the `!`
suffix.

This design constraint helps distinguish header fields from struct fields.
Headers significantly differ from structs in that any undeclared field is valid
at runtime, something strictly disallowed with normal structs. When users see
the `@` prefix, they know they are working with headers, a pseudo-struct where
everything is optional, and new runtime fields are not disallowed.

### What headers should I define in the schema?

Define all headers that clients might be expected to use directly. If a client
is supposed to send a header, inspect a header, or otherwise rely on it as part
of the API contract, it should be present in the schema.

If a header is only used to pass data between server transports, middleware,
and function handlers, but the header is never actually exposed to the client
on the wire, do not define it in the schema since that will distract clients.

### Why does my unauthenticated server fail to start?

Telepact server libraries default to requiring the standard `union.Auth_`
definition. If `union.Auth_` is not defined, the server will
error on startup, prompting the implementer to either define `union.Auth_`
or use the server options to indicate auth is not required.

This startup check forces the implementer to make conscientious decisions
about the auth configuration of their server.

### What does transport-agnostic mean in practice?

Telepact defines the message format, schema, validation, and ecosystem
features, but it does not define the transport itself. If you choose HTTP,
WebSockets, NATS, stdio, or something else, that transport remains yours to
implement and operate.

This is intentional. Telepact's goal is bring-your-own-transport, not
transport abstraction. So implementers keep both the freedom and the
responsibility that come with their chosen transport.

For concrete HTTP and WebSocket examples, see the
[Transport Guide](#transport-guide).

### Why are there no transport adapters included with Telepact?

Telepact intentionally does not ship a first-party transport abstraction layer
for the common case. In practice, bytes in and bytes out is not much
boilerplate, and it preserves clarity at a critical component boundary.

Because of that, Telepact prefers to keep the transport layer explicit rather
than wrap it in a heavier abstraction that obscures how the system is actually
wired. For examples of what that explicit code looks like in practice, see the
[Transport Guide](#transport-guide).

### Why can I not define nullable arrays or objects?

Nullability is indicated on base types by appending type strings with `?`, but
since collection types are defined with native JSON array and object syntax,
using `[]` and `{}` respectively, there is no way to append `?` to these
expressions since free `?` characters are not legal JSON syntax.

This apparent design constraint, albeit coincidental, aligns with Telepact's
design goals of expressibility without redundant design options. In Telepact,
null represents "empty" (while optional represents "unknown"). Since array and
object collection types can already express "emptiness," nullability is
unnecessary.

### Why is there nothing like a standard 404 Not Found error?

Telepact provides several standard errors to represent common integration
issues, such as request and response incompatibilities and
authentication/authorization errors, all reminisicent of the 400, 500, 401 and
403 error codes, respectively, but there is no standard error that approximates
404 Not Found.

Instead, API designers are encouraged to abstract concepts as data whenever
possible, and the 404 Not Found use-case can be trivially represented with an
empty optional value.

### But the given 400-like Bad Request errors are too precise. Why is a more general-purpose "Bad Request" error not available?

Telepact has several errors to communicate request invalidity with respect to
the API schema, but there is no out-of-the-box "Bad Request" error that a server
can raise from some custom validation logic in server middleware or a function
route.

Overly generalized abstractions, such as a catch-all "Bad Request", are
unpreferred in Telepact in favor of precise data types. Where necessary, all
"Bad Request" use-cases can be enumerated in function results alongside the
`Ok_` tag. API designers are encouraged to prefer data abstractions over errors
wherever possible, such as preferring empty optionals over "Not Found" errors.

### Isn't `ErrorUnknown_` too opaque to be useful?

Telepact intentionally keeps unexpected server failures opaque on the wire.
Exposing server-side implementation details to clients is usually the wrong
default, much like how HTTP `500` communicates that the server failed without
dumping local internals into the response.

`ErrorUnknown_` follows that model on purpose, but it still improves on a plain
`500`: the response includes a `caseId`. That gives clients an always-on handle
they can report to server operators, who can then match that `caseId` against
local logs and recover the real stack trace or diagnostic context without
turning those internal details into part of the public API contract.

### Why do functions in Telepact not support positional arguments?

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

### Why is there no Enum type as seen in C or Java?

Telepact achieves enumerated types with unions, which are very similar to enums
as seen in C or Java, except that a struct is automatically attached to each
value. The traditional enum can be approximated by simply leaving all union
structs blank.

### Why force servers to perform response validation?

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

### If all I want is compact binary serialization, why not just use gRPC?

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

### Why can't I have other non-error result union values?

The only required tag for the function result union is `Ok_`. All other tags in
the result union that are not `Ok_` are, by definition, "not okay", and will be
interpreted as an error in all circumstances. API designers are encouraged to
prefix additional result union tags with `Error` or equivalent to improve
readability and recognition of errors.

### Why can't I associate a union tag to something besides a struct?

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

### Why can I not omit fn.\* fields using the `"@select_"` header?

The `"@select_"` header is used to omit fields from the response result graph:
the active result union, reachable structs, and reachable union payload
structs. It does not apply to the argument struct included with function
definitions.

The function type exists so that API providers may incorporate "links" into
their API design, such that the appearance of a function type payload can simply
be copied and pasted verbatim into the body a new message. Tooling like the
Telepact console specifically utilizes this technique to allow end-users to
"click through" graphs designed by the API provider.

Omitting fields in the argument struct disrupts the API provider's ability to
established well-defined links, and consequently, the `"@select_"` header is
disallowed from omitting fields in function argument structs.

## Motivation

### Principles

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

### Summary

| Capability                                        | OpenAPI | JSON-RPC | gRPC | GraphQL | Telepact |
| ------------------------------------------------- | ------- | -------- | ---- | ------- | -------- |
| No transport restrictions                         | ❌      | 🤔       | ❌   | 🤔      | ✅       |
| No transport details leaked into API              | ❌      | ✅       | ✅   | ✅      | ✅       |
| Out-of-band headers/metadata                      | ✅      | ❌       | ✅   | 🤔      | ✅       |
| No string parsing/splicing                        | ❌      | ✅       | ✅   | ✅      | ✅       |
| Low development burden for servers                | ✅      | ✅       | ✅   | ❌      | ✅       |
| No required libraries for clients                 | ✅      | ✅       | ❌   | ❌      | ✅       |
| Type-safe generated code                          | 🤔      | ❌       | ✅   | ✅      | ✅       |
| Human-editable wire-format                        | ✅      | ✅       | ❌   | 🤔      | ✅       |
| Built-in binary data serialization protocol       | ❌      | ❌       | ✅   | ❌      | ✅       |
| Built-in dynamic response shaping                 | ❌      | ❌       | ❌   | ✅      | ✅       |
| No required ABI                                   | ✅      | ✅       | ❌   | ✅      | ✅       |
| Expressive distinction between null and undefined | ❌      | ❌       | ❌   | ❌      | ✅       |
| Built-in API documentation distribution           | 🤔      | ❌       | ❌   | ✅      | ✅       |
| Built-in mocking for tests                        | ❌      | ❌       | ❌   | ❌      | ✅       |

### Why not RESTful APIs?

RESTful APIs are familiar to many developers and are highly accessible due to
reliance on ubiquitous tooling like HTTP and JSON. However, RESTful APIs rely on
HTTP and cannot be used across other IPC boundaries, limiting their use. RESTful
APIs also tend to leak transport details into the API definition itself, which
often leads to design inefficiencies where API design is stalled to answer
HTTP-specific questions, such as determining the right url structure, query
parameters, HTTP method, HTTP status code, etc. Type-safe code generation for
RESTful APIs is in development with OAS and is generally available with
limitations.

### Why not JSON-RPC?

JSON-RPC is an approachable RPC style because it keeps requests and responses
in plain JSON and can be layered on top of almost any transport. However,
JSON-RPC has no standard pattern for metadata, so integrations that require
metadata are restricted to transports that support it (e.g. http has headers,
websockets do not). JSON-RPC intentionally does not define a schema/IDL, so
type validation, documentation, code completion, code generation, mocking, and
backwards-compatible evolution are typically handled by separate tools or ad-hoc
conventions that drift over time. JSON-RPC also does not provide built-in
mechanisms for binary serialization or dynamic response shaping, so performance
optimizations often reintroduce custom protocol work at the application layer.

### Why not gRPC?

gRPC APIs are highly efficient and leverage critical improvements offered by the
HTTP/2 specification. They are also type-safe through generated code boundaries
derived from a wholistic IDL that does not leak transport details. However, gRPC
lacks overall accessibility due to reliance on heavy toolchains with generated
code in a finite number of programming languages. And there are some API design
limitations with gRPC, such as prohibitive rules with lists (i.e. repeated
values), a lack of distinction between null and undefined, and a weak error
model at the protocol layer which has prompted patching at the library level
with limited coverage across the gRPC ecosystem.

### Why not GraphQL?

GraphQL is a unique API technology that features a custom query language to
dynamically build data payloads from a pre-crafted set of server-side functions.
GraphQL itself is transport-agnostic, but in practice it is most commonly used
over HTTP and WebSockets. While consumption of the "graph" is extremely expressive
for clients, construction of the graph's backing functions places a modest burden
on server-side development to properly and efficiently integrate the query engine
with the backing database. GraphQL also has limited accessibility as clients
largely rely on GraphQL libraries to construct the query strings so as to
minimize parse error risk. GraphQL does feature a rich data model, but it lacks
support for common programming idioms, such as dictionaries. While binary
serialization is technically possible through manual configuration, it is
largely not observed in practice due to the accessibility tax it would incur on
both servers and clients.

### Why Telepact?

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
