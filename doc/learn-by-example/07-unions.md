# 07. Unions

A union is a sum type. On the wire, Telepact represents it with a tagged-object
pattern: one uppercase tag, plus the fields that belong to that tag.

The demo schema defines `union.Expression` like this:

```json
{
  "union.Expression": [
    {
      "Constant": {
        "value": "number"
      }
    },
    {
      "Variable": {
        "name": "string"
      }
    },
    {
      "Add": {
        "left": "union.Expression",
        "right": "union.Expression"
      }
    },
    ...
  ]
}
```

That union is then reused inside `struct.Evaluation`, which is what
`fn.getPaperTape` returns:

```json
{
  "struct.Evaluation": {
    "expression": "union.Expression",
    "result": "number?",
    "timestamp": "integer",
    "successful": "boolean"
  }
}
```

As a quick baseline, `fn.add` does not use a union in its arguments:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.add": {"x": 2, "y": 3}}]'
```

```json
[{}, {"Ok_": {"result": 5}}]
```

To see a union on the wire, let's evaluate one expression and then read the
paper tape.

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "union-guide"}}}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "result": 5,
      "saveResult": {
        "fn.saveVariable": {
          "name": "result",
          "value": 5
        }
      }
    }
  }
]
```

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "union-guide"}}}, {"fn.getPaperTape": {"limit!": 1}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "tape": [
        {
          "expression": {
            "Add": {
              "left": {
                "Constant": {
                  "value": 2
                }
              },
              "right": {
                "Constant": {
                  "value": 3
                }
              }
            }
          },
          "result": 5,
          "timestamp": 1775686282,
          "successful": true
        }
      ]
    }
  }
]
```

The important part is that only one tag shows up for any given union value.
Here the outer expression uses `Add`, while the nested children use `Constant`.
We never see two tags competing in the same union instance.

Next, let's put the pieces together and talk about functions in
[08-functions.md](./08-functions.md).
