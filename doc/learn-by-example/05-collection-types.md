# 05. Schema: Collection types

Now let's add collections to our type-expression toolbox.

## Start the demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## The two collection forms

- `[]` means an array
- `{}` means an object

In Telepact object type expressions, the key type is always `string`, because JSON object keys are strings.

## Find collection examples in `fn.api_`

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {}}]'
```

```jsonc
{
  "fn.deleteVariables": {
    "names": ["string"]
  },
  "fn.saveVariables": {
    "variables": {"string": "number"}
  },
  "fn.evaluate": {
    "->": [
      {
        "ErrorUnknownVariables": {
          "unknownVariables": ["string"]
        }
      }
    ]
  }
}
```

## Use an object collection

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.saveVariables": {"variables": {"a": 2, "b": 4}}}]'
```

```json
[{}, {"Ok_": {}}]
```

## Use an array collection

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.deleteVariables": {"names": ["a", "b"]}}]'
```

```json
[{}, {"Ok_": {}}]
```

There is no nullable collection syntax like `[]?` or `{}?`. That's intentional: an empty collection already expresses “nothing here” without adding another null case.

Next: [06. Structs](./06-structs.md)
