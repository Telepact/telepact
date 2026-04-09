# 08. Function

Let's put the schema pieces together into Telepact's main unit of interaction:
a function.

## Start a fresh demo server

```sh
telepact demo-server --port 8007
```

A function has two halves:

- an argument struct under `fn.*`
- a result union under `->`

Here is `fn.evaluate`:

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

A few important things are happening here:

- `Ok_` is the required success tag
- the other tags are function-specific errors
- `saveResult` is a **link** because it uses `fn.saveVariable` as a type
  expression

Let's see the happy path first:

```sh
curl -s http://127.0.0.1:8007/api -X POST -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 5, "saveResult": {"fn.saveVariable": {"name": "result", "value": 5}}}}]
```

That `saveResult` payload is already a ready-to-send Telepact call.

Now let's trigger the error tags.

Unknown variables:

```sh
curl -s http://127.0.0.1:8007/api -X POST -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Variable": {"name": "missing"}}, "right": {"Constant": {"value": 1}}}}}}]'
```

```json
[{}, {"ErrorUnknownVariables": {"unknownVariables": ["missing"]}}]
```

Divide by zero:

```sh
curl -s http://127.0.0.1:8007/api -X POST -d '[{}, {"fn.evaluate": {"expression": {"Div": {"left": {"Constant": {"value": 6}}, "right": {"Constant": {"value": 0}}}}}}]'
```

```json
[{}, {"ErrorCannotDivideByZero": {}}]
```

Optional `!` fields can also appear inside function-shaped definitions, such as
`limit!` on `fn.getPaperTape` and `variable!` inside the `Ok_` result of
`fn.getVariable`.

Next: [09. Service errors](./09-service-errors.md)
