# 10. Comments

Let's notice one small but important quality-of-life feature: schema comments.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's inspect the schema:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {}}]'
```

A schema entry can include a `///` key:

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

That `///` value is informational only. It helps humans and tools explain the
API, but it does not change request or response validation.

We can prove that nothing special happens on the wire by calling the function as
usual:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

```json
[{}, {"Ok_": {"result": 3}}]
```

Any struct-like definition can use `///`, so when we are exploring a Telepact
API, those comments are worth reading closely.

Next: [11. Select](./11-opt-in-select.md)
