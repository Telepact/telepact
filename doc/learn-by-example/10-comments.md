# 10. Schema: Comments

Let's finish the schema tour with the simplest feature: comments.

## Start the demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Look for `///`

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {}}]'
```

```jsonc
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

Any struct-like schema definition can carry a `///` docstring key.

That comment is informational only. It helps readers and tools, but it does not change what clients send or what servers return.

For example, this request still works exactly the same way:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.add": {"x": 2, "y": 3}}]'
```

```json
[{}, {"Ok_": {"result": 5}}]
```

Next: [11. Select](./11-select.md)
