# 02. Getting started: Schema

Now let's ask the server to describe itself.

## Start the demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Call `fn.api_`

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {}}]'
```

The response is long, so let's zoom in on one entry:

```jsonc
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

This schema is the whole interface surface area. If we can read this, we can discover what the server accepts and returns.

## Call one schema-defined function

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.add": {"x": 2, "y": 3}}]'
```

```json
[{}, {"Ok_": {"result": 5}}]
```

## Notice the trailing underscore

Anything with a trailing underscore is an internal definition.

- `fn.ping_` and `fn.api_` come stock with Telepact servers
- `fn.add` was defined by this server's author

If we want to see internal definitions too, we can opt in:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

That's how we discover built-in headers, built-in validation errors, and other internal types.

Next: [03. Data type validation](./03-data-type-validation.md)
