# 09. Service Errors

So far we have looked at errors attached to one function. Now let's look at
errors that belong to the whole service.

## Start a fresh demo server

```sh
telepact demo-server --port 8008
```

Ask for internal definitions so we can see the shared error set:

```sh
curl -s http://127.0.0.1:8008/api -X POST -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Schema excerpt:

```json
{
  "errors.Availability": [
    {
      "ErrorUnavailable": {}
    }
  ]
}
```

This looks just like a union definition because it is doing a similar job:
listing possible error tags. The difference is scope. Anything inside an
`errors.*` definition is available across the whole service.

That makes `ErrorUnavailable` a good example. It is broad. It is not tied to the
business rules of one specific function.

Two design notes are worth carrying forward:

- using `errors.*` for placeholders like 404-style "not found" is an
  anti-pattern in Telepact
- using `errors.*` for generic 400-style input problems is also unnecessary,
  because Telepact already validates request types for us

Instead, Telepact pushes us toward patterns like:

- optional fields for "not found", as in `fn.getVariable`
- function-specific error tags for business rules, such as
  `ErrorCannotDivideByZero`

Next: [10. Comments](./10-comments.md)
