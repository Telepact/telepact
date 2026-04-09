# 08. Schema: Function

Let's put the pieces together.

## Start the demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Read a function definition

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {}}]'
```

```jsonc
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

A function is an argument struct on the left and a result union under `->`.

- the `Ok_` tag is always required
- non-`Ok_` tags are the function's error results
- `saveResult` shows that a `fn.*` definition can also be used as a type expression, which acts like a pre-filled link

## See the link-shaped `saveResult`

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 5, "saveResult": {"fn.saveVariable": {"name": "result", "value": 5}}}}]
```

That nested value is ready to be followed as another Telepact call.

## See the error cases

Unknown variable:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.evaluate": {"expression": {"Variable": {"name": "z"}}}}]'
```

```json
[{}, {"ErrorUnknownVariables": {"unknownVariables": ["z"]}}]
```

Divide by zero:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.evaluate": {"expression": {"Div": {"left": {"Constant": {"value": 8}}, "right": {"Constant": {"value": 0}}}}}}]'
```

```json
[{}, {"ErrorCannotDivideByZero": {}}]
```

We also still see the optional `!` notation in struct-like places such as `limit!`, `variable!`, and auth error `message!` fields.

Next: [09. Service errors](./09-service-errors.md)
