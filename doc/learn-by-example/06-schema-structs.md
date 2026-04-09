# 06. Structs

Let's move from loose collections to fixed shapes.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's inspect the parts of the schema we care about:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {}}]'
```

`struct.Variable` is a struct definition:

```json
{
  "struct.Variable": {
    "name": "string",
    "value": "number"
  }
}
```

Its lowercase keys, `name` and `value`, are fields. Together they define a JSON
object with a fixed shape.

Now let's see where that struct gets reused:

```json
{
  "fn.getVariable": {
    "name": "string"
  },
  "->": [
    {
      "Ok_": {
        "variable!": "struct.Variable"
      }
    }
  ]
}
```

Let's store a variable, then fetch it back.

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.saveVariable": {"name": "answer", "value": 42}}]'

curl -s http://localhost:8000/api \
  --data '[{}, {"fn.getVariable": {"name": "answer"}}]'
```

```json
[{}, {"Ok_": {"variable!": {"name": "answer", "value": 42}}}]
```

By default, struct fields are required. The `!` suffix changes that: it makes a
field optional, which means it may be omitted on the wire.

We can see that right away in `variable!`. If the variable does not exist, the
server simply omits the field:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.getVariable": {"name": "missing"}}]'
```

```json
[{}, {"Ok_": {}}]
```

That is Telepact's preferred shape for "maybe there is a value": keep the outer
result successful, and make the field optional.

Next: [07. Union](./07-schema-union.md)
