# 13. Mock server

Let's keep the demo server running on port 8000, and start a mock server in a
second terminal:

```sh
telepact mock --http-url http://localhost:8000/api --port 8080
```

This mock server absorbs the live server's schema, so it can simulate that
integration locally with schema validation intact.

That is the normal client-side pattern Telepact encourages:

- use a mock while integrating
- either point the mock at a live Telepact server
- or fetch the schema once with `telepact fetch` and mock from the cached copy

If we call `fn.api_` on the mock server, we get the same public schema surface:

```sh
curl -s localhost:8080/api -d '[{}, {"fn.api_": {}}]' | python -m json.tool
```

```json
{
  "///": "A function that adds two numbers.",
  "fn.add": {
    "x": "number",
    "y": "number"
  },
  "->": [
    {
      "Ok_": {
        "result": "number"
      }
    }
  ]
}
```

But if we include internal definitions, the mock exposes much more than the live
demo server did, including mock-control functions:

```sh
curl -s localhost:8080/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]' | python -m json.tool
```

```json
{
  "fn.createStub_": {
    "stub": "_ext.Stub_",
    "strictMatch!": "boolean",
    "count!": "integer"
  },
  "->": [
    {
      "Ok_": {}
    }
  ]
}
```

Those extra definitions are what make the mock so useful for downstream client
work.

Next, let's see what the mock does before we configure anything in
[14-stock-mock.md](./14-stock-mock.md).
