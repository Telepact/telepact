# 02. Schema

Now let's ask the server to describe itself.

## Start a fresh demo server

```sh
telepact demo-server --port 8001
```

Then ask for the schema:

```sh
curl -s http://127.0.0.1:8001/api -X POST -d '[{}, {"fn.api_": {}}]'
```

The full response is large, so let's zoom in on one useful slice:

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

That schema entry defines the whole contract for `fn.add`: what arguments the
client may send, and what result shape the server may return.

Let's call it:

```sh
curl -s http://127.0.0.1:8001/api -X POST -d '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

```json
[{}, {"Ok_": {"result": 3}}]
```

A useful naming convention appears here too:

- names ending in `_` are **internal** Telepact definitions
- names without that trailing `_` belong to the service author

So `fn.ping_` and `fn.api_` come with Telepact, while `fn.add` was defined by
this server.

If we want to see internal definitions too, we can ask for them explicitly:

```sh
curl -s http://127.0.0.1:8001/api -X POST -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Next: [03. Data type validation](./03-data-type-validation.md)
