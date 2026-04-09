# 03. Getting started: Data type validation

Now let's look at one of Telepact's biggest promises: validation comes with the server.

## Start the demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Find `fn.saveVariable` in the schema

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {}}]'
```

Let's focus on this one function:

```jsonc
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

The lowercase keys `name` and `value` are **fields**.

The values after those fields are **type expressions**:

- `"string"`
- `"number"`

## Send bad data on purpose

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.saveVariable": {"name": 1, "value": "nope"}}]'
```

```json
[{}, {"ErrorInvalidRequestBody_": {"cases": [{"path": ["fn.saveVariable", "name"], "reason": {"TypeUnexpected": {"actual": {"Number": {}}, "expected": {"String": {}}}}}, {"path": ["fn.saveVariable", "value"], "reason": {"TypeUnexpected": {"actual": {"String": {}}, "expected": {"Number": {}}}}}]}}]
```

That validation behavior is a core part of Telepact. Servers always do it, so clients can trust the pattern.

We *could* learn a Telepact service through trial and error alone, but learning to read the schema is the smoother next step.

Next: [04. Scalar types](./04-scalar-types.md)
