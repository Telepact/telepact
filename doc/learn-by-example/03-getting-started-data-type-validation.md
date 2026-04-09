# 03. Data type validation

Let's stay with `fn.api_`, but this time let's read it as a contract.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's inspect the `fn.saveVariable` part of the schema:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {}}]'
```

Relevant excerpt:

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

Here, `name` and `value` are **fields**: non-qualified lowercase keys. Their
values, `string` and `number`, are **type expressions**.

Let's break the contract on purpose:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.saveVariable": {"name": 1, "value": "oops"}}]'
```

Response:

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

This validation is not a custom extra. It is a core part of Telepact, and it
comes for free on Telepact servers. That gives clients a pattern they can trust:
if the schema says a field is a `string`, the runtime will enforce it.

We really could learn a Telepact API through trial and error alone, but reading
`fn.api_` is the much friendlier next step.

Next: [04. Scalar types](./04-schema-scalar-types.md)
