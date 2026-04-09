# 11. Select

Now let's step into our first opt-in feature: field selection.

## Start a fresh demo server

```sh
telepact demo-server --port 8010
```

To see the selection header, we need internal definitions:

```sh
curl -s http://127.0.0.1:8010/api -X POST -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Schema excerpt:

```json
{
  "headers.Select_": {
    "@select_": "_ext.Select_"
  },
  "->": {}
}
```

For the full rules behind `_ext.Select_`, see the select section of the
[Extensions guide](../extensions.md#_extselect_).

Let's first make a normal `fn.evaluate` call:

```sh
curl -s http://127.0.0.1:8010/api -X POST -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 7}}, "right": {"Constant": {"value": 8}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 15, "saveResult": {"fn.saveVariable": {"name": "result", "value": 15}}}}]
```

Now let's ask for only the `result` field from the `Ok_` payload:

```sh
curl -s http://127.0.0.1:8010/api -X POST -d '[{"@select_": {"->": {"Ok_": ["result"]}}}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 7}}, "right": {"Constant": {"value": 8}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 15}}]
```

The server computed the same result. We simply opted out of receiving the
`saveResult` field.

Next: [12. Binary](./12-binary.md)
