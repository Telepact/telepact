# 08. Functions

In Telepact, a function is an argument struct plus a result union.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Read a function definition

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

The function entrypoint itself defines the argument struct. The `->` entrypoint
defines the result union.

`Ok_` is always required. Everything else is treated as an error result.

## Links

Notice `saveResult` uses `fn.saveVariable` as a type expression. That is a link:
the server is returning a prepopulated future call shape.

Let's see it:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 4}}}}}}]'
```

```json
[
  {},
  {
    "Ok_": {
      "result": 6,
      "saveResult": {
        "fn.saveVariable": {
          "name": "result",
          "value": 6
        }
      }
    }
  }
]
```

## Error cases

Unknown variable:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Variable": {"name": "missing"}}}}]'
```

```json
[{}, {"ErrorUnknownVariables": {"unknownVariables": ["missing"]}}]
```

Divide by zero:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Div": {"left": {"Constant": {"value": 4}}, "right": {"Constant": {"value": 0}}}}}}]'
```

```json
[{}, {"ErrorCannotDivideByZero": {}}]
```

## Optional fields in function-shaped definitions

Optional fields still use `!`, even inside function arguments:

```json
{
  "fn.getPaperTape": {
    "limit!": "integer"
  }
}
```

So both of these are valid:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.getPaperTape": {}}]'
curl -s localhost:8000/api -d '[{}, {"fn.getPaperTape": {"limit!": 1}}]'
```

Next: [09. Service errors](./09-service-errors.md)
