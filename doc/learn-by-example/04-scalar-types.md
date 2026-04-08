# 04. Scalar types

Let's start reading the schema vocabulary from the inside out.

These are Telepact's scalar type expressions:

| Type expression | Meaning |
| --- | --- |
| `boolean` | `true` or `false` |
| `integer` | whole numbers |
| `number` | JSON numbers, including non-integers |
| `string` | JSON strings |
| `?` suffix | nullable scalar, such as `number?` |

We can spot all of them in the demo schema:

```json
{
  "fn.api_": {
    "includeInternal!": "boolean"
  }
}
```

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
  "fn.getPaperTape": {
    "limit!": "integer"
  }
}
```

```json
{
  "struct.Evaluation": {
    "result": "number?",
    "timestamp": "integer",
    "successful": "boolean"
  }
}
```

```json
{
  "fn.login": {
    "username": "string"
  }
}
```

Let's touch a few of those on the wire.

A `number` request and response:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.add": {"x": 2, "y": 3}}]'
```

```json
[{}, {"Ok_": {"result": 5}}]
```

A `string` request and response:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.login": {"username": "scalar-guide"}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "token": "<random string>"
    }
  }
]
```

And a stateful response that includes `integer`, `number`, and `boolean`
values together:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "scalar-guide"}}}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]' > /dev/null
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "scalar-guide"}}}, {"fn.getPaperTape": {"limit!": 1}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "tape": [
        {
          "result": 5,
          "timestamp": 1775686282,
          "successful": true
        }
      ]
    }
  }
]
```

Notice that `number?` means `result` is allowed to be `null`, even though this
particular successful evaluation returned a real number.

Next, let's add the collection forms in
[05-collection-types.md](./05-collection-types.md).
