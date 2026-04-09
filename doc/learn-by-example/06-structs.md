# 06. Structs

Let's move from open-ended collections to fixed-shape objects.

## Start a fresh demo server

```sh
telepact demo-server --port 8005
```

A Telepact struct is a JSON object with a fixed set of lowercase fields:

```json
{
  "struct.Variable": {
    "name": "string",
    "value": "number"
  }
}
```

We can also see that struct used as a type expression inside `fn.getVariable`:

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

The `!` on `variable!` means the field is optional, so it may be omitted on the
wire.

Let's make that concrete.

Save a variable first:

```sh
curl -s http://127.0.0.1:8005/api -X POST -d '[{}, {"fn.saveVariable": {"name": "a", "value": 2}}]'
```

```json
[{}, {"Ok_": {}}]
```

Now read it back:

```sh
curl -s http://127.0.0.1:8005/api -X POST -d '[{}, {"fn.getVariable": {"name": "a"}}]'
```

```json
[{}, {"Ok_": {"variable!": {"name": "a", "value": 2}}}]
```

And now ask for a missing variable:

```sh
curl -s http://127.0.0.1:8005/api -X POST -d '[{}, {"fn.getVariable": {"name": "missing"}}]'
```

```json
[{}, {"Ok_": {}}]
```

That last response is the optional-field pattern in action: omission, not a 404,
and not `null`.

Next: [07. Union](./07-union.md)
