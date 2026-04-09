# 08. Function

Let's put the pieces together and look at a full Telepact function definition.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's inspect `fn.evaluate`:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {}}]'
```

Relevant excerpt:

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

A Telepact function has two parts:

- the `fn.*` entrypoint is an argument struct
- the `->` entrypoint is a result union

The `Ok_` tag is always required. Everything else in the result union is an
error result.

Let's see the happy path first:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.saveVariables": {"variables": {"a": 2, "b": 4}}}]'

curl -s http://localhost:8000/api \
  --data '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Variable": {"name": "a"}}, "right": {"Variable": {"name": "b"}}}}}}]'
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

`saveResult` is a link-like value. Its type is `fn.saveVariable`, so the server
is returning a prepopulated function call we could follow later.

Now let's trigger both error tags:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.evaluate": {"expression": {"Variable": {"name": "missing"}}}}]'
```

```json
[{}, {"ErrorUnknownVariables": {"unknownVariables": ["missing"]}}]
```

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.evaluate": {"expression": {"Div": {"left": {"Constant": {"value": 1}}, "right": {"Constant": {"value": 0}}}}}}]'
```

```json
[{}, {"ErrorCannotDivideByZero": {}}]
```

We can also see optional `!` notation in function-shaped definitions. For
example, `fn.getPaperTape` has `limit!`, so we may omit it, and `fn.api_` has
`includeInternal!` and `includeExamples!` for the same reason.

Next: [09. Service errors](./09-schema-service-errors.md)
