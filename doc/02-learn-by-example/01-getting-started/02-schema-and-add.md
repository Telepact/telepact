# 02. Schema and `fn.add`

Now let's ask the server to describe itself.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Call `fn.api_`

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {}}]'
```

The response is large, so let's focus on the part that matters for `fn.add`:

```json
[
  {},
  {
    "Ok_": {
      "api": [
        ...,
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
        },
        ...
      ]
    }
  }
]
```

This schema is the whole interface surface area of the server. If we can read the
schema, we can discover the API without guessing.

## Call `fn.add`

Request:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

Response:

```json
[{}, {"Ok_": {"result": 3}}]
```

## Internal names end with `_`

This is a good moment to notice a naming pattern:

- `fn.ping_` and `fn.api_` end with `_`, so they are **internal**
- `fn.add` does not end with `_`, so it was defined by the service author

Every Telepact server comes with stock internal definitions like `fn.ping_` and
`fn.api_`. Service authors add their own public definitions beside them.

If we want to see the internal definitions too, we can ask for them:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Next: [03. Data type validation](03-data-type-validation.md)
