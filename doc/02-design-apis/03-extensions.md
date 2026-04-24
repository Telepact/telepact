# Extensions

Telepact reserves `_ext.*_` names for internal extension types. These are not
normal schema definitions for API authors to invent freely; they are built-in
placeholders that Telepact libraries interpret with custom validation and
example-generation logic.

## Why Extensions Exist

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

## How Extensions Deviate From Normal Patterns

- Their definitions are placeholders, not full declarative schemas.
- Their valid shape is derived from nearby schema content or the active
  function, not only from the `_ext.*_` entry itself.
- They are implemented by Telepact libraries directly.
- They are intended for internal and mock-control workflows, not as a general
  schema authoring pattern.

If you need ordinary API data modeling, use `struct.*`, `union.*`, `fn.*`,
`headers.*`, and `errors.*`.

## Discovering Them

Call `fn.api_` with `{"includeInternal!": true}` to include internal schemas,
including `_ext.*_` definitions. Add `{"includeExamples!": true}` to get
deterministic example payloads for those types.

The examples below are illustrative request and response messages. They use the
normal Telepact two-object message format:

```json
[
  {
    "@header_": "value"
  },
  {
    "fn.someCall": {}
  }
]
```

## Extension Guides

- [`_ext.Select_`](./04-select-extension.md) covers the `@select_` header and
  response-shaping payloads.
- [Mock extensions](./05-mock-extensions.md) covers `_ext.Call_`,
  `_ext.Stub_`, and how `fn.verify_` consumes `_ext.Call_`.

## Practical Guidance

- Prefer ordinary Telepact definitions unless you are intentionally integrating
  with Telepact internal or mock schemas.
- Treat `_ext.*_` types as reserved names with runtime-defined behavior.
- When in doubt, inspect `fn.api_` with internal definitions and examples
  enabled to see the exact shape the current schema exposes.
