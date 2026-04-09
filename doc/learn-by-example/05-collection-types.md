# 05. Collection Types

Now let's add the two collection shapes: arrays and objects.

## Start a fresh demo server

```sh
telepact demo-server --port 8004
```

These schema excerpts show both collection types with scalar values:

```json
{
  "fn.deleteVariables": {
    "names": ["string"]
  }
}
```

```json
{
  "fn.saveVariables": {
    "variables": {
      "string": "number"
    }
  }
}
```

A few things to notice:

- `[]` means an array type
- `{}` means an object type
- object keys are always `string`, because JSON object keys are strings

Let's use both of them.

An object of scalar values:

```sh
curl -s http://127.0.0.1:8004/api -X POST -d '[{}, {"fn.saveVariables": {"variables": {"a": 2, "b": 4}}}]'
```

```json
[{}, {"Ok_": {}}]
```

An array of scalar values:

```sh
curl -s http://127.0.0.1:8004/api -X POST -d '[{}, {"fn.deleteVariables": {"names": ["a", "b"]}}]'
```

```json
[{}, {"Ok_": {}}]
```

One subtle rule matters here: Telepact does not have nullable collection syntax.
We cannot write something like `[]?` or `{}?`. That is intentional. Collections
already have a natural "empty" value: length zero.

Next: [06. Structs](./06-structs.md)
