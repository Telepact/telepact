# 06. Structs

A struct is a product type: one JSON object with a fixed set of fields.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Look at `struct.Variable`

```json
{
  "struct.Variable": {
    "name": "string",
    "value": "number"
  }
}
```

The lowercase keys `name` and `value` are the fields.

Now let's see where that struct is reused:

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

## Save a variable, then read it back

```sh
curl -s localhost:8000/api -d '[{}, {"fn.saveVariable": {"name": "x", "value": 3}}]'
curl -s localhost:8000/api -d '[{}, {"fn.getVariable": {"name": "x"}}]'
```

Response:

```json
[{}, {"Ok_": {"variable!": {"name": "x", "value": 3}}}]
```

## Optional fields use `!`

That `variable!` field is optional. If the variable is missing, the field is
simply omitted on the wire:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.getVariable": {"name": "missing"}}]'
```

```json
[{}, {"Ok_": {}}]
```

So in Telepact:

- fields are required by default
- `!` means the field is optional and may be omitted entirely

Next: [07. Unions](./07-unions.md)
