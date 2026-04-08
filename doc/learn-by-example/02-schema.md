# 02. Schema

Now that we can reach the server, let's ask it for its schema.

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {}}]' | python -m json.tool
```

The real response is long, so let's focus on one strategic excerpt:

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

That `api` array is the interface surface area of the server. If we can read
the schema, we can discover what the server accepts and what it can return.

Let's immediately use the `fn.add` definition we just found:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.add": {"x": 2, "y": 3}}]'
```

```json
[{}, {"Ok_": {"result": 5}}]
```

This is also a nice place to notice the naming pattern: anything with a
trailing underscore is an internal definition. So `fn.ping_` and `fn.api_`
come stock with Telepact servers, while `fn.add` was defined by the server
implementer.

If we want to see the internal definitions too, we opt in with the optional
`includeInternal!` flag:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

That expanded schema includes the built-in definitions that normal clients do
not usually need to read first.

Next, let's watch the schema drive automatic request validation in
[03-data-type-validation.md](./03-data-type-validation.md).
