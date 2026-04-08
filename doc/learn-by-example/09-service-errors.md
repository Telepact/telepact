# 09. Service errors

Some errors are not about one business rule. They can happen anywhere in the
service.

In the demo schema, that looks like this:

```json
{
  "errors.Availability": [
    {
      "ErrorUnavailable": {}
    }
  ]
}
```

That shape looks like a union because it works like one: every tag listed in an
`errors.*` definition gets added to every user-defined function in the service.

The demo server uses this to model broad availability trouble, not a
function-specific rule. A sample response looks like this:

```json
[{}, {"ErrorUnavailable": {}}]
```

That is a good use of `errors.*`: something systemic that could surface from
anywhere.

Telepact discourages using `errors.*` for placeholder patterns like `404 Not
Found` or `400 Bad Request`.

- "not found" is usually better modeled as optional data, like `variable!` on
  `fn.getVariable`
- request-shape problems are already covered by built-in validation, such as
  `ErrorInvalidRequestBody_`
- everything else should usually be a function-specific error, like
  `ErrorCannotDivideByZero`

Next, let's finish the schema tour with comments in
[10-comments.md](./10-comments.md).
