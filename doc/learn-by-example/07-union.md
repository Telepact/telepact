# 07. Union

Now let's learn the other big schema shape: a tagged union.

## Start a fresh demo server

```sh
telepact demo-server --port 8006
```

A Telepact union is a JSON object where exactly one uppercase tag appears at a
time.

Here is the key idea from `union.Expression`:

```json
{
  "union.Expression": [
    {"Constant": {"value": "number"}},
    {"Variable": {"name": "string"}},
    {"Add": {"left": "union.Expression", "right": "union.Expression"}},
    {"Sub": {"left": "union.Expression", "right": "union.Expression"}},
    {"Mul": {"left": "union.Expression", "right": "union.Expression"}},
    {"Div": {"left": "union.Expression", "right": "union.Expression"}}
  ]
}
```

And here is one place it gets used:

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

Let's send one concrete union instance through `fn.evaluate`:

```sh
curl -s http://127.0.0.1:8006/api -X POST -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 5, "saveResult": {"fn.saveVariable": {"name": "result", "value": 5}}}}]
```

Now let's inspect the tape entry that was recorded:

```sh
curl -s http://127.0.0.1:8006/api -X POST -d '[{}, {"fn.getPaperTape": {"limit!": 1}}]'
```

```json
[{}, {"Ok_": {"tape": [{"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}, "result": 5, "timestamp": ..., "successful": true}]}}]
```

Notice that this union instance contains only one tag: `Add`. That is the union
pattern: one tag, one payload, at a time.

Next: [08. Function](./08-function.md)
