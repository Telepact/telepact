# 10. Comments

Let's look at one small but useful schema feature: comments.

## Start a fresh demo server

```sh
telepact demo-server --port 8009
```

Schema entries can carry a `///` key for documentation.

For example, the `fn.add` entry includes a docstring:

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

And union tags can be commented too:

```json
{
  "///": "A constant numeric `value`.",
  "Constant": {
    "value": "number"
  }
}
```

These comments are informational only. They help humans and tooling, but they do
not change what requests and responses are valid.

We can prove that quickly by still calling `fn.add` exactly the same way:

```sh
curl -s http://127.0.0.1:8009/api -X POST -d '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

```json
[{}, {"Ok_": {"result": 3}}]
```

Next: [11. Select](./11-select.md)
