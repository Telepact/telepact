# 06. Schema: Structs

Let's meet Telepact's product type: the struct.

## Start the demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Find `struct.Variable`

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {}}]'
```

```jsonc
{
  "struct.Variable": {
    "name": "string",
    "value": "number"
  },
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

A struct is a JSON object with a fixed key shape. Its lowercase keys are fields, and each field points to a type expression.

## Save a struct-shaped value, then read it back

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.saveVariable": {"name": "x", "value": 4}}]'
```

```json
[{}, {"Ok_": {}}]
```

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.getVariable": {"name": "x"}}]'
```

```json
[{}, {"Ok_": {"variable!": {"name": "x", "value": 4}}}]
```

## Notice `!` on a field name

Fields are required by default.

When a field name ends in `!`, it is optional on the wire. We can see that in `variable!` above. If the variable is missing, the field is simply omitted:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.getVariable": {"name": "missing"}}]'
```

```json
[{}, {"Ok_": {}}]
```

Next: [07. Union](./07-union.md)
