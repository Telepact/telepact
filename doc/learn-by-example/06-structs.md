# 06. Structs

A struct is a product type: a JSON object with a fixed key shape.

In Telepact, the lowercase keys inside that shape are fields, and each field
points to a type expression.

The demo server defines this struct:

```json
{
  "struct.Variable": {
    "name": "string",
    "value": "number"
  }
}
```

We can also see the struct reused as a type expression here:

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

Fields are required by default. The `!` suffix means the field is optional on
the wire, so `variable!` may be omitted entirely.

The demo server protects stateful functions, so we'll use the lightweight
`Ephemeral` auth variant here and keep our attention on the struct shape.

First let's save a variable:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "struct-guide"}}}, {"fn.saveVariable": {"name": "pi", "value": 3.14}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {}
  }
]
```

Then let's read it back:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "struct-guide"}}}, {"fn.getVariable": {"name": "pi"}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "variable!": {
        "name": "pi",
        "value": 3.14
      }
    }
  }
]
```

And if the variable is missing, the optional field disappears instead of turning
into a `404`-style error:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "struct-guide"}}}, {"fn.getVariable": {"name": "missing"}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {}
  }
]
```

Next, let's look at the tagged shape Telepact uses for alternatives in
[07-unions.md](./07-unions.md).
