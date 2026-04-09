# 04. Scalar types

Let's start reading Telepact type expressions from the inside out.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's ask for the schema:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {}}]'
```

## The scalar type expressions

| Type expression | Meaning |
| --- | --- |
| `boolean` | `true` or `false` |
| `integer` | a whole number |
| `number` | any JSON number |
| `string` | a JSON string |
| `?` suffix | `null` is also allowed |

Here are a few real examples from the demo schema:

```json
{
  "fn.login": {
    "username": "string"
  }
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

Now let's see those scalar values on the wire.

A `string` request field and a `string` response field:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.login": {"username": "demo-user"}}]'
```

```json
[{}, {"Ok_": {"token": "...random token..."}}]
```

An `integer` argument:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.getPaperTape": {"limit!": 1}}]'
```

A `number` result:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

```json
[{}, {"Ok_": {"result": 3}}]
```

And a `boolean` plus an `integer` in a response:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 1}}, "right": {"Constant": {"value": 2}}}}}}]'

curl -s http://localhost:8000/api \
  --data '[{}, {"fn.getPaperTape": {"limit!": 1}}]'
```

```json
[
  {},
  {
    "Ok_": {
      "tape": [
        {
          "result": 3,
          "timestamp": 1775748910,
          "successful": true
        }
      ]
    }
  }
]
```

The `number?` form means `null` would also be valid there. This demo happens to
return numbers for `result`, but the schema still tells us that `null` would be
allowed too.

Next: [05. Collection types](./05-schema-collection-types.md)
