# 02. Schema

Now let's ask the server to describe itself.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's call `fn.api_`:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {}}]'
```

The real response is long, so let's zoom in on the part that defines `fn.add`:

```json
[
  {},
  {
    "Ok_": {
      "api": [
        ...,
        {
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
        },
        ...
      ]
    }
  }
]
```

This schema is the interface surface area of the whole service. If we can read
it, we can discover what functions exist, what arguments they accept, and what
results they may return.

Now let's call `fn.add` itself:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

Response:

```json
[{}, {"Ok_": {"result": 3}}]
```

A useful naming rule appears here too: names with a trailing underscore `_` are
internal definitions. So `fn.ping_` and `fn.api_` come stock with Telepact,
while `fn.add` was defined by this particular server.

If we want to see internal definitions too, we can opt in:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

That is a nice pattern to remember: Telepact gives us a built-in way to inspect
both the public surface and the internal platform features.

Next: [03. Data type validation](./03-getting-started-data-type-validation.md)
