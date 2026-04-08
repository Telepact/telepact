# 03. Data type validation

Let's stay with `fn.api_`, but this time we'll zoom in on one function that
has obvious field types.

```json
{
  "fn.saveVariable": {
    "name": "string",
    "value": "number"
  },
  "->": [
    {
      "Ok_": {}
    }
  ]
}
```

Here `name` and `value` are fields because they are lowercase keys with no
prefix like `fn.` or `struct.`. The strings after them are type expressions:
`string` and `number`.

Let's break that contract on purpose:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.saveVariable": {"name": 123, "value": "oops"}}]' | python -m json.tool
```

```json
[
  {},
  {
    "ErrorInvalidRequestBody_": {
      "cases": [
        {
          "path": ["fn.saveVariable", "name"],
          "reason": {
            "TypeUnexpected": {
              "actual": {"Number": {}},
              "expected": {"String": {}}
            }
          }
        },
        {
          "path": ["fn.saveVariable", "value"],
          "reason": {
            "TypeUnexpected": {
              "actual": {"String": {}},
              "expected": {"Number": {}}
            }
          }
        }
      ]
    }
  }
]
```

This validation is not a special case that this demo server happened to add.
It comes with Telepact itself, so clients can rely on it across compliant
servers.

We could learn a lot through trial and error alone, but now the natural next
step is to read the schema directly.

Next, let's map out the scalar type language in
[04-scalar-types.md](./04-scalar-types.md).
