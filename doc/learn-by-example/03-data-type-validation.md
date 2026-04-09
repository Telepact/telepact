# 03. Data type validation

Let's look at one of Telepact's biggest promises: predictable validation.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Find `fn.saveVariable` in the schema

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {}}]'
```

The part we care about looks like this:

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

Here, `name` and `value` are **fields**:

- they are lowercase
- they are not qualified with a prefix like `fn.` or `struct.`

And their values are **type expressions**:

- `string`
- `number`

## Send the wrong types

```sh
curl -s localhost:8000/api -d '[{}, {"fn.saveVariable": {"name": 123, "value": "oops"}}]'
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

This validation comes for free. Telepact servers always do it, which means
clients can trust the pattern.

We *could* learn a service by trial and error like this, but now we're ready for
the nicer path: learning to read the schema directly.

Next: [04. Scalar types](./04-scalar-types.md)
