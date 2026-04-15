# 11. Comments

Telepact schemas can carry comments directly inside the schema entries.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Look for `///`

When we call `fn.api_`, we see entries like this:

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

That `///` key is just a comment. Any struct-like definition can have one:

- `fn.*`
- `struct.*`
- `union.*`
- `headers.*`
- `errors.*`

These comments are informational only. They help people and tools, but they do
not change request or response behavior.

Next: [12. Select](../03-opt-in-features/12-select.md)
