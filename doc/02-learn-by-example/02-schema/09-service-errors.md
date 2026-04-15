# 09. Service errors

Some errors belong to one function. Others can happen anywhere in a service.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Look at `errors.Availability`

```json
{
  "errors.Availability": [
    {
      "ErrorUnavailable": {}
    }
  ]
}
```

This shape looks just like a union definition, but it behaves differently:
everything declared here is added to every service function.

That is why `ErrorUnavailable` can appear broadly across the demo service.

## What service errors are for

This kind of definition is for service-wide concerns, like availability.

It is **not** the place for placeholder errors like:

- "404 Not Found"
- "400 Bad Request"

Telepact steers us away from both:

- for "not found", prefer expressive data like an optional field, as in
  `fn.getVariable`
- for request-shape problems, Telepact already gives us built-in validation
  errors like `ErrorInvalidRequestBody_`
- for business-rule failures, define function-specific errors like
  `ErrorCannotDivideByZero`

Next: [10. Headers](10-headers.md)
