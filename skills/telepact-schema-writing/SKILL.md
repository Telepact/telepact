---
name: telepact-schema-writing
description: Convert a plain-English API description into a correct Telepact schema, usually authored as `.telepact.yaml`. Use when agent needs to design or revise Telepact schema files, choose between structs, unions, functions, errors, and headers, and emit valid Telepact type expressions and docstrings.
---

# Telepact Schema Writing

Use this skill when the task is: "Here is the API I want; write the Telepact schema."

The goal is to turn a plain-English description into a valid Telepact schema file with minimal assumptions, good naming, and correct Telepact semantics.

## Workflow

1. Identify the API surface from the user's description.
2. Extract functions first: verbs usually become `fn.*` definitions.
3. Extract shared data models next: reusable records become `struct.*`; closed variants become `union.*`.
4. Decide whether any cross-cutting headers or systemic errors are needed.
5. Emit a schema array with one top-level definition object per item.
6. Add concise docstrings when they improve readability. Prefer YAML block scalars for multi-line docstrings.
7. Before finishing, validate the schema against the checklist in this file.

If the description is underspecified, prefer one short clarifying question only when the ambiguity changes the contract materially. Otherwise make the narrowest reasonable assumption and state it briefly.

## Output Shape

By default, write checked-in schemas as `.telepact.yaml`. Use `.telepact.json`
only when the user explicitly asks for JSON or when an inline JSON example is
more precise for the explanation.

A Telepact schema is semantically a JSON-shaped array:

```yaml
- info.Example: {}
- fn.doThing: {}
  "->":
    - Ok_: {}
```

Each array item is one top-level definition object.

Recommended ordering:

1. `info.*`
2. `headers.*`
3. `errors.*`
4. `fn.*`
5. `struct.*`
6. `union.*`

Match nearby repo examples if the user is editing an existing schema.

## Type Expressions

Telepact types are written as JSON strings, arrays, or objects.

### Scalar Types

Use these scalar type strings:

- `boolean`
- `integer`
- `number`
- `string`
- `any`
- `bytes`

Use `integer` for counts, IDs that must stay numeric, and timestamps.
Use `number` for fractional values.
Use `string` for names, tokens, textual IDs, and enums that should stay open-ended.
Use `bytes` for binary payloads.
Use `any` only when the API truly accepts arbitrary JSON-like values.

### References

These type strings refer to other definitions:

- `struct.Name`
- `union.Name`
- `fn.name`

Telepact also has internal `_ext.*` types such as `_ext.Select_`, but do not author them unless the task explicitly requires Telepact internal or mock-selection behavior.

### Arrays

An array type is a single-element JSON array whose element is another type expression:

```json
["string"]
["struct.User"]
["union.Event?"]
```

### Maps / Dynamic Objects

A dynamic object type is a JSON object with exactly one key, and that key must be `"string"`:

```json
{"string": "integer"}
{"string": "struct.User"}
{"string": ["number"]}
```

This means "an object whose keys are strings and whose values match the inner type."

### Nesting

Type expressions can nest:

```json
[{"string": "boolean"}]
{"string": ["struct.User"]}
[["integer"]]
{"string": {"string": "any"}}
```

### Nullability

Append `?` to a type string to allow `null`:

```json
"string?"
"struct.Profile?"
"union.Result?"
"fn.nextPage?"
```

Important:

- `?` applies to type strings, not to arrays or objects themselves.
- `["string?"]` means an array whose elements may be `null`.
- You cannot write a nullable array or nullable map directly.

## Top-Level Definitions

The main Telepact definition kinds are `info`, `struct`, `union`, `fn`, `errors`, and `headers`.

### `info.Name`

Use one `info.*` definition near the top of the schema as a simple schema identity or overview marker.

Pattern:

```json
{
    "///": " A calculator app that provides basic math computation capabilities. ",
    "info.Calculator": {}
}
```

Keep it empty: `{}`.

### `struct.Name`

A struct is a product type: a JSON object with named fields.

Pattern:

```json
{
    "struct.User": {
        "id": "string",
        "email": "string",
        "displayName!": "string",
        "avatarUrl!": "string?"
    }
}
```

Rules:

- Fields without `!` are required.
- Fields with `!` are optional and may be omitted entirely.
- The `!` stays in the schema field name.
- The JSON payload also uses that exact field name.
- Optional and nullable are different:
  - `name!`: field may be omitted.
  - `name: "string?"`: field is required but may be `null`.
  - `"name!": "string?"`: field may be omitted, and if present may be `null`.

Use a struct when the concept is a reusable record with a stable set of fields.

### `union.Name`

A union is a tagged sum type. It is a JSON array of tag objects. Each tag has one key, and that key maps to a struct-like object.

Pattern:

```json
{
    "union.PaymentMethod": [
        {
            "Card": {
                "last4": "string"
            }
        },
        {
            "BankAccount": {
                "bankName": "string"
            }
        },
        {
            "Cash": {}
        }
    ]
}
```

Rules:

- A union must have at least one tag.
- Each runtime value must choose exactly one tag.
- Tag payloads may have required and optional fields just like a struct.
- Empty tags use `{}`.

Use a union when a value can take one of several closed, explicitly tagged variants.

### `fn.name`

A function defines a request struct and a response union.

Pattern:

```json
{
    "fn.createUser": {
        "email": "string",
        "displayName!": "string"
    },
    "->": [
        {
            "Ok_": {
                "user": "struct.User"
            }
        },
        {
            "ErrorEmailTaken": {}
        }
    ]
}
```

Rules:

- The function arguments are a struct-like object.
- The result under `"->"` is a union.
- The result union must include `Ok_`.
- Non-`Ok_` tags are errors by convention.
- Use `"Ok_": {}` for command-style success with no result payload.
- Function types may be referenced elsewhere as `fn.name`.
- When a function type is referenced as a type, only its argument shape matters.
- Do not place function types inside the top-level argument tree of another function.

Good defaults:

- Reads usually return data inside `Ok_`.
- Writes usually return `{}` or the created/updated record.
- Pagination or follow-up actions can use function-type links when useful.

### `errors.Name`

An `errors.*` definition adds the same error tags to every user-defined function in the schema.

Pattern:

```json
{
    "errors.General": [
        {
            "ErrorRateLimited": {
                "retryAfterSeconds!": "integer"
            }
        },
        {
            "ErrorInternal": {
                "message!": "string"
            }
        }
    ]
}
```

Rules:

- `errors.*` looks like a union, but it is not referenced by type.
- These tags are appended to all user-defined function result unions.
- Use this only for systemic, cross-cutting server failures.

Do not use `errors.*` to model routine domain states such as "not found", "empty search result", or "already deleted" unless the user explicitly wants that contract. Prefer expressive data, for example:

- an optional result field
- an empty array
- a union in the `Ok_` payload

### `headers.Name`

Headers definitions describe request and response headers.

Pattern:

```json
{
    "headers.Auth": {
        "@requestId": "string",
        "@traceId": "string"
    },
    "->": {
        "@ratelimitRemaining": "integer"
    }
}
```

Rules:

- Every header field name must start with `@`.
- All header fields are implicitly optional.
- Do not add `!` to header field names.
- Extra unspecified header fields are allowed.
- `headers.*` cannot be referenced in type expressions.

Use `headers.*` only for true message metadata: auth, tracing, idempotency, rate-limit headers, and similar transport-level concerns.

## Docstrings

Top-level definitions and union tags may include a `///` docstring.

Single-line:

```yaml
"///": " A user record. "
struct.User:
  id: string
```

Multi-line:

```yaml
"///": |
  A user record.

  Used in account flows.
struct.User:
  id: string
```

Use docstrings when the schema will be read by humans in the Telepact console or checked into the repo long term. Keep them short and factual. In real schema files, prefer YAML for docstring-heavy definitions.

## Automatic Definitions

Do not re-declare Telepact's built-in definitions.

### Standard Definitions

Telepact automatically adds standard helpers and common errors such as `fn.ping_`, `ErrorInvalidRequest`, and `ErrorUnknown_`.

### Auth Definitions

If the API needs Telepact-standard auth, define a non empty `struct.Auth_`.

Example:

```json
{
    "struct.Auth_": {
        "token": "string"
    }
}
```

This enables Telepact auth definitions such as the `@auth_` header and auth-related errors. Put auth-related credential data inside `struct.Auth_`.

### Mock Definitions

Mock-only definitions such as `fn.createStub_` and `fn.verify_` are added when served through a `MockServer`. Do not author them in normal application schemas.

## Plain English To Schema Mapping

Use these translation rules when converting a description into schema:

- "Create", "update", "delete", "list", "get", "search", "send" usually become `fn.*`.
- Repeated nouns with multiple fields become `struct.*`.
- "Either X or Y", "one of", "variant", "kind", "status-specific payload" usually becomes `union.*`.
- "Dictionary", "map", "lookup by name", "arbitrary keys" usually becomes `{"string": T}`.
- "List of" usually becomes `[T]`.
- "Optional" means field-name `!`, not `?`.
- "Can be null" means append `?` to the type string.
- "Header", "token", "trace id", "request id" may require `headers.*`.
- "Applies to every function" may require `errors.*`, but only for systemic failures.

## Design Heuristics

- Prefer shared `struct.*` definitions when the same object shape appears in more than one place.
- Prefer `union.*` over free-form strings when the set of cases is closed and each case may have its own payload.
- Prefer data-rich success responses over generic errors.
- Prefer narrow types over `any`.
- Keep function names verb-like and data type names noun-like.
- Use `Ok_` payloads that return domain objects, not transport details.
- Keep headers out of normal business payloads.

## Authoring Template

Use this template when drafting from scratch:

```yaml
- "///": " One-line API summary. "
  info.ApiName: {}
- "///": " One-line function summary. "
  fn.example:
    requiredField: string
    optionalField!: integer
  "->":
    - Ok_:
        result: struct.Result
- "///": " One-line shared type summary. "
  struct.Result:
    id: string
```

## Final Validation Checklist

Before returning the schema, verify:

- The file is a schema array semantically, even if authored in YAML.
- Every top-level entry is one valid definition object.
- All type strings are valid Telepact types.
- Optional fields use `!` on the field name.
- Nullable types use `?` on the type string.
- Arrays use `[T]`.
- Dynamic objects use `{"string": T}`.
- Every `fn.*` has a `"->"` result union.
- Every function result union contains `Ok_`.
- Every union has at least one tag.
- Every header field begins with `@`.
- `errors.*` is used only for cross-cutting failures.
- DO NOT define your own "404 Not Found" or "400 Bad Request." Telepact handles those types of errors for you.
- No built-in Telepact definitions were redundantly re-declared.
- The schema matches the user's API description without inventing unnecessary features.

When the user asks for the finished schema, return the complete `.telepact.yaml` content by default, and include only brief assumptions outside the schema. Use `.telepact.json` only when the user explicitly asks for JSON.
