# 07. Unions

A union is a tagged choice. Exactly one tag shows up at a time.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Look at `union.Expression`

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

Uppercase keys are the tags. Inside each tag, lowercase keys are fields again.

Now let's see where that union is used:

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

And `struct.Evaluation` is returned by `fn.getPaperTape`.

## Make one union value, then read it back

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
curl -s localhost:8000/api -d '[{}, {"fn.getPaperTape": {"limit!": 1}}]'
```

Example response:

```json
[
  {},
  {
    "Ok_": {
      "tape": [
        {
          "expression": {
            "Add": {
              "left": {"Constant": {"value": 2}},
              "right": {"Constant": {"value": 3}}
            }
          },
          "result": 5,
          "timestamp": 1744221600,
          "successful": true
        }
      ]
    }
  }
]
```

Only one tag appears in that instance of `union.Expression`: `Add`.

Next: [08. Functions](./08-functions.md)
