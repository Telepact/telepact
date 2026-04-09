# 03. Data Type Validation

Now let's watch Telepact reject bad data before service logic even gets a turn.

## Start a fresh demo server

```sh
telepact demo-server --port 8002
```

First, let's inspect the part of the schema we care about:

```sh
curl -s http://127.0.0.1:8002/api -X POST -d '[{}, {"fn.api_": {}}]'
```

Schema excerpt:

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

In Telepact terms:

- `name` and `value` are **fields**
- a field is a non-qualified lowercase key
- the strings after those fields are **type expressions**

So here the two type expressions are `string` and `number`.

Let's break the contract on purpose:

```sh
curl -s http://127.0.0.1:8002/api -X POST -d '[{}, {"fn.saveVariable": {"name": 42, "value": "oops"}}]'
```

```json
[{}, {"ErrorInvalidRequestBody_": {"cases": [{"path": ["fn.saveVariable", "name"], "reason": {"TypeUnexpected": {"actual": {"Number": {}}, "expected": {"String": {}}}}}, {"path": ["fn.saveVariable", "value"], "reason": {"TypeUnexpected": {"actual": {"String": {}}, "expected": {"Number": {}}}}}]}}]
```

This validation is a built-in Telepact behavior. Telepact servers always do it,
which means clients can trust that schemas and validation line up.

We *could* learn a service by trial and error like this. But now that we have
seen the validator, the natural next move is to read the schema directly.

Next: [04. Scalar types](./04-scalar-types.md)
