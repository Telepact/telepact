# 07. Union

Now let's look at Telepact's tagged union pattern.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's inspect the expression type and where it gets used:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {}}]'
```

Here is the heart of `union.Expression`:

```json
{
  "union.Expression": [
    {"Constant": {"value": "number"}},
    {"Variable": {"name": "string"}},
    {"Add": {"left": "union.Expression", "right": "union.Expression"}},
    ...
  ]
}
```

This is a union type: a JSON object where exactly one uppercase key is present.
That uppercase key is the **tag**, and the lowercase keys inside it are fields.

We can also see the union reused here:

```json
{
  "struct.Evaluation": {
    "expression": "union.Expression",
    "result": "number?",
    "timestamp": "integer",
    "successful": "boolean"
  }
}
```

And `struct.Evaluation` shows up in `fn.getPaperTape`.

Because the paper tape records evaluations, let's make one first:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 1}}, "right": {"Constant": {"value": 2}}}}}}]'

curl -s http://localhost:8000/api \
  --data '[{}, {"fn.getPaperTape": {"limit!": 1}}]'
```

```json
[
  {},
  {
    "Ok_": {
      "tape": [
        {
          "expression": {
            "Add": {
              "left": {"Constant": {"value": 1}},
              "right": {"Constant": {"value": 2}}
            }
          },
          "result": 3,
          "timestamp": 1775748910,
          "successful": true
        }
      ]
    }
  }
]
```

Only one tag appears in each union instance. Here the outer union instance is an
`Add`, and each child is a `Constant`. That tagged-struct pattern is how
Telepact expresses "one of several possible shapes".

Next: [08. Function](./08-schema-function.md)
