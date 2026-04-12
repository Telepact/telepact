# 05. Collection types

Now let's add the two collection forms.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## The collection type expressions

| Type expression | Meaning |
| --- | --- |
| `["string"]` | array of strings |
| `{"string": "number"}` | object whose keys are strings and whose values are numbers |

That object key is always `string`, because JSON object keys are strings.

## Where they show up in the demo schema

```json
{
  "fn.deleteVariables": {
    "names": ["string"]
  },
  "fn.saveVariables": {
    "variables": {"string": "number"}
  }
}
```

## Real examples

### Array

```sh
curl -s localhost:8000/api -d '[{}, {"fn.deleteVariables": {"names": ["a", "b"]}}]'
```

```json
[{}, {"Ok_": {}}]
```

### Object

```sh
curl -s localhost:8000/api -d '[{}, {"fn.saveVariables": {"variables": {"a": 2, "b": 4}}}]'
```

```json
[{}, {"Ok_": {}}]
```

### Empty collections are already expressive

Both of these are still valid:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.deleteVariables": {"names": []}}]'
curl -s localhost:8000/api -d '[{}, {"fn.saveVariables": {"variables": {}}}]'
```

That is why Telepact does not try to express nullable collections like `[]?` or
`{}?`. Emptiness already has a natural representation.

Next: [06. Structs](./06-structs.md)
