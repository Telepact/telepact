# 10. Comments

Any struct-like definition in a Telepact schema can carry a `///` comment.

Here are two examples from the demo schema:

```json
{
  "///": "A function that adds two numbers.",
  "fn.add": {
    "x": "number",
    "y": "number"
  }
}
```

```json
{
  "///": "A constant numeric `value`.",
  "Constant": {
    "value": "number"
  }
}
```

Those comments help humans, code generators, consoles, and docs, but they do
not change request or response validation.

We can prove that by making an ordinary call. The comments do not appear on the
wire here:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.add": {"x": 2, "y": 3}}]'
```

```json
[{}, {"Ok_": {"result": 5}}]
```

So `///` enriches the schema, but not the runtime message format.

Next, let's move into opt-in client features with field selection in
[11-select.md](./11-select.md).
