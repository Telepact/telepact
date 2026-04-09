# 07. Schema: Union

Now let's look at Telepact's tagged sum type: the union.

## Start the demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Find `union.Expression`

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {}}]'
```

```jsonc
{
  "union.Expression": [
    {"Constant": {"value": "number"}},
    {"Variable": {"name": "string"}},
    {"Add": {"left": "union.Expression", "right": "union.Expression"}},
    ...
  ],
  "struct.Evaluation": {
    "expression": "union.Expression",
    "result": "number?",
    "timestamp": "integer",
    "successful": "boolean"
  },
  "fn.getPaperTape": {
    "->": [
      {
        "Ok_": {
          "tape": ["struct.Evaluation"]
        }
      }
    ]
  }
}
```

Union tags are uppercase keys like `Constant`, `Variable`, and `Add`. In any one union instance, only one tag appears.

## Create one union value, then read it back

`fn.getPaperTape` records evaluations, so let's use `fn.evaluate` first:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 5, "saveResult": {"fn.saveVariable": {"name": "result", "value": 5}}}}]
```

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.getPaperTape": {"limit!": 1}}]'
```

```jsonc
[{}, {"Ok_": {"tape": [{"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}, ...}]}}]
```

That `expression` value shows exactly one union tag: `Add`.

Next: [08. Function](./08-function.md)
