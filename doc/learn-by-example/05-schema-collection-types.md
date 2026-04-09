# 05. Collection types

Now let's add the two collection shapes: arrays and objects.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's inspect the schema again:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Here are three useful excerpts:

```json
{
  "fn.saveVariables": {
    "variables": {"string": "number"}
  }
}
```

```json
{
  "fn.deleteVariables": {
    "names": ["string"]
  }
}
```

```json
{
  "headers.Binary_": {
    "@bin_": ["integer"]
  }
}
```

A few rules fall out of those examples:

- `[]` means an array
- `{}` means an object
- object keys are always `string`, because JSON object keys are strings
- Telepact does not have nullable collections like `[]?` or `{}?`
- that is intentional, because an empty array or empty object already expresses
  "nothing here" without adding a nullable collection form

Let's send one object collection and one array collection.

An object of scalar values:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.saveVariables": {"variables": {"a": 2, "b": 4}}}]'
```

```json
[{}, {"Ok_": {}}]
```

An array of scalar values:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.deleteVariables": {"names": ["a", "b"]}}]'
```

```json
[{}, {"Ok_": {}}]
```

So collection types are still built out of the same idea we already know: type
expressions, now wrapped in JSON arrays or JSON objects.

Next: [06. Structs](./06-schema-structs.md)
