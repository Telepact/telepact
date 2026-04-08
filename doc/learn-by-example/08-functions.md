# 08. Functions

A Telepact function is an argument struct plus a result union.

We can see that pattern in a few different places:

```json
{
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

```json
{
  "fn.getVariable": {
    "name": "string"
  },
  "->": [
    {
      "Ok_": {
        "variable!": "struct.Variable"
      }
    }
  ]
}
```

```json
{
  "fn.evaluate": {
    "expression": "union.Expression"
  },
  "->": [
    {
      "Ok_": {
        "result": "number",
        "saveResult": "fn.saveVariable"
      }
    },
    {
      "ErrorUnknownVariables": {
        "unknownVariables": ["string"]
      }
    },
    {
      "ErrorCannotDivideByZero": {}
    }
  ]
}
```

The lower-case keys in the `fn.*` definition are argument fields. The `->`
section is a union definition. `Ok_` is always required, and the other tags are
the function's error outcomes.

`fn.evaluate` also shows that a function definition can be reused as a type
expression. The `saveResult` field is a ready-made `fn.saveVariable` call.

Let's see the success case:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "function-guide"}}}, {"fn.evaluate": {"expression": {"Mul": {"left": {"Constant": {"value": 6}}, "right": {"Constant": {"value": 7}}}}}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "result": 42,
      "saveResult": {
        "fn.saveVariable": {
          "name": "result",
          "value": 42
        }
      }
    }
  }
]
```

Now the function-specific error cases:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "function-guide"}}}, {"fn.evaluate": {"expression": {"Variable": {"name": "missing"}}}}]' | python -m json.tool
```

```json
[
  {},
  {
    "ErrorUnknownVariables": {
      "unknownVariables": ["missing"]
    }
  }
]
```

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "function-guide"}}}, {"fn.evaluate": {"expression": {"Div": {"left": {"Constant": {"value": 1}}, "right": {"Constant": {"value": 0}}}}}}]' | python -m json.tool
```

```json
[
  {},
  {
    "ErrorCannotDivideByZero": {}
  }
]
```

Optional `!` notation also appears in function-like shapes. For example,
`limit!` on `fn.getPaperTape` is an optional argument field, and `variable!` on
`fn.getVariable` is an optional result field.

Next, let's zoom out from function-specific errors to service-wide ones in
[09-service-errors.md](./09-service-errors.md).
