# 04. Scalar Types

Let's start reading Telepact type expressions one family at a time.

## Start a fresh demo server

```sh
telepact demo-server --port 8003
```

## The scalar type expressions

| Type expression | Meaning |
| --- | --- |
| `boolean` | `true` or `false` |
| `integer` | whole numbers only |
| `number` | JSON numbers, including decimals |
| `string` | JSON strings |
| `?` | allows `null` on a scalar type |

A few schema highlights from `fn.api_`:

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
  },
  "->": [
    {
      "Ok_": {
        "token": "string"
      }
    }
  ]
}
```

## Real requests and responses

A `number` in action:

```sh
curl -s http://127.0.0.1:8003/api -X POST -d '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

```json
[{}, {"Ok_": {"result": 3}}]
```

A `string` in action:

```sh
curl -s http://127.0.0.1:8003/api -X POST -d '[{}, {"fn.login": {"username": "alice"}}]'
```

```json
[{}, {"Ok_": {"token": "..."}}]
```

An `integer` and a `boolean` in action:

```sh
curl -s http://127.0.0.1:8003/api -X POST -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
curl -s http://127.0.0.1:8003/api -X POST -d '[{}, {"fn.getPaperTape": {"limit!": 1}}]'
```

```json
[{}, {"Ok_": {"tape": [{"expression": {"Add": {...}}, "result": 5, "timestamp": ..., "successful": true}]}}]
```

The `?` in `number?` means `result` is allowed to be `null`, even though this
demo service happens to fill it with a number in the response above.

Next: [05. Collection types](./05-collection-types.md)
