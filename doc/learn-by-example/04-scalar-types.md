# 04. Schema: Scalar types

Let's start reading Telepact type expressions from the inside out.

## Start the demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## The scalar type expressions

| Type expression | Meaning |
| --- | --- |
| `boolean` | `true` or `false` |
| `integer` | whole numbers |
| `number` | JSON numbers |
| `string` | JSON strings |
| `?` suffix | `null` is also allowed |

## Find a few examples in `fn.api_`

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {}}]'
```

```jsonc
{
  "fn.login": {
    "username": "string"
  },
  "fn.getPaperTape": {
    "limit!": "integer"
  },
  "struct.Evaluation": {
    "result": "number?",
    "timestamp": "integer",
    "successful": "boolean"
  }
}
```

## See those types on the wire

A `string` argument:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.login": {"username": "alice"}}]'
```

```json
[{}, {"Ok_": {"token": "<token>"}}]
```

An `integer` argument and a `boolean` field in the response:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.getPaperTape": {"limit!": 1}}]'
```

```jsonc
[{}, {"Ok_": {"tape": [{"timestamp": 1775747725, "successful": true, ...}]}}]
```

The demo schema also says `result` is `number?`. This demo server happens to send numbers there, but the `?` tells us `null` would also be valid.

Next: [05. Collection types](./05-collection-types.md)
