# 11. Select

Sometimes we know we will not need every field in a response. Telepact lets us
opt in to field selection with the `@select_` header.

If we ask for internal definitions, we can see that header in the schema:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]' | python -m json.tool
```

```json
{
  "headers.Select_": {
    "@select_": "_ext.Select_"
  },
  "->": {}
}
```

For the full selection shape, let's keep the schema open beside
[the `_ext.Select_` section of `extensions.md`](../extensions.md#_extselect_).

First, here is an ordinary `fn.evaluate` response:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "select-guide"}}}, {"fn.evaluate": {"expression": {"Mul": {"left": {"Constant": {"value": 6}}, "right": {"Constant": {"value": 7}}}}}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "result": 42,
      "saveResult": {
        "fn.saveVariable": {
          "name": "result",
          "value": 42
        }
      }
    }
  }
]
```

Now let's ask only for `result`:

```sh
curl -s localhost:8000/api -d '[{"@auth_": {"Ephemeral": {"username": "select-guide"}}, "@select_": {"->": {"Ok_": ["result"]}}}, {"fn.evaluate": {"expression": {"Mul": {"left": {"Constant": {"value": 6}}, "right": {"Constant": {"value": 7}}}}}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "result": 42
    }
  }
]
```

The server still computed the same result. We simply trimmed the response graph
so the `saveResult` field was omitted.

Next, let's opt into Telepact's binary mode in
[12-binary.md](./12-binary.md).
