# 04. Scalar types

Let's start reading the schema in smaller pieces.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## The scalar type expressions

| Type expression | Meaning |
| --- | --- |
| `boolean` | `true` or `false` |
| `integer` | whole number |
| `number` | JSON number |
| `string` | JSON string |
| `bytes` | binary data |

Nullability is written with a `?` suffix, like `number?` or `string?`.

## Where they show up in the demo schema

```json
{
  "fn.add": {"x": "number", "y": "number"},
  "fn.getPaperTape": {"limit!": "integer"},
  "fn.login": {"username": "string"},
  "struct.Evaluation": {
    "result": "number?",
    "timestamp": "integer",
    "successful": "boolean"
  },
  "fn.export": {},
  "->": [{"Ok_": {"blob": "bytes"}}]
}
```

## Real examples

### `number`

```sh
curl -s localhost:8000/api -d '[{}, {"fn.add": {"x": 1.5, "y": 2}}]'
```

```json
[{}, {"Ok_": {"result": 3.5}}]
```

### `integer`, `boolean`, and nullable `number?`

Let's create one evaluation and then read it back:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Constant": {"value": 7}}}}]'
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
          "expression": {"Constant": {"value": 7}},
          "result": 7,
          "timestamp": 1744221600,
          "successful": true
        }
      ]
    }
  }
]
```

### `bytes`

```sh
curl -s localhost:8000/api -d '[{}, {"fn.export": {}}]'
```

Example response:

```json
[
  {
    "@base64_": {
      "Ok_": {
        "blob": true
      }
    }
  },
  {
    "Ok_": {
      "blob": "gql2YXJpYWJsZXO..."
    }
  }
]
```

The schema says `bytes`, but JSON has no raw bytes type, so Telepact coerces the
wire value to Base64.

Next: [05. Collection types](05-collection-types.md)
