# 05. Collection types

Now let's add the two collection shapes:

- arrays use `[]`
- objects use `{}`

In object type expressions, the key type is always `string`, because JSON only
supports string keys.

Here are two clean examples from the demo schema:

```json
{
  "fn.saveVariables": {
    "variables": {
      "string": "number"
    }
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

Let's send both shapes.

An object collection:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "collection-guide"}}}, {"fn.saveVariables": {"variables": {"x": 10, "y": 20}}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {}
  }
]
```

An array collection:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "collection-guide"}}}, {"fn.deleteVariables": {"names": ["x", "y"]}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {}
  }
]
```

One subtle rule matters here: collections are not nullable. We do not write
`[]?` or `{ }?`. That is intentional, because collections already have a built-in
empty value: length zero.

Next, let's move from free-form collections to fixed-shape objects in
[06-structs.md](./06-structs.md).
