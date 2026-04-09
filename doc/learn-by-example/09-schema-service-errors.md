# 09. Service errors

Let's separate per-function errors from service-wide errors.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's inspect the service errors definition:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {}}]'
```

Relevant excerpt:

```json
{
  "errors.Availability": [
    {
      "ErrorUnavailable": {}
    }
  ]
}
```

That shape looks just like a union definition, and the idea is similar too. The
important difference is scope: every tag listed in an `errors.*` definition gets
added to every function in the service.

So `ErrorUnavailable` is not a business-rule error for one function. It is a
broad system-level error that could show up anywhere.

This is also a good place to notice two Telepact design preferences:

- using `errors.*` for placeholder reusable errors like "404 Not Found" is an
  anti-pattern
- using `errors.*` for something like "400 Bad Request" is unnecessary, because
  Telepact already has built-in request validation

Instead, Telepact encourages:

- optional fields for "maybe no data exists", like `variable!` in
  `fn.getVariable`
- function-specific errors for real business rules, like
  `ErrorCannotDivideByZero`

So service errors are for service-wide concerns, not for sweeping all domain
errors into one shared bucket.

Next: [10. Comments](./10-schema-comments.md)
