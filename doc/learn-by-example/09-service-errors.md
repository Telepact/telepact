# 09. Schema: Service errors

Let's separate service-wide errors from function-specific errors.

## Start the demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Find `errors.Availability`

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {}}]'
```

```jsonc
{
  "errors.Availability": [
    {
      "ErrorUnavailable": {}
    }
  ]
}
```

This definition has the same shape as a union, but it means something different: every entry in `errors.*` gets added to every user-defined function in the service.

So `ErrorUnavailable` is not tied to one business rule. It is a broad “the service can't help right now” error that could appear anywhere.

A sample response would look like this:

```json
[{}, {"ErrorUnavailable": {}}]
```

## Use service errors sparingly

This is a good fit for broad issues like availability.

It is an anti-pattern to use `errors.*` for placeholders like “404 Not Found” or “400 Bad Request”.

- Telepact already covers bad input with validation errors
- “not found” is often better modeled as optional data, like `fn.getVariable` returning `Ok_` without `variable!`
- function-specific business rules should stay on that function, like `ErrorCannotDivideByZero`

Next: [10. Comments](./10-comments.md)
