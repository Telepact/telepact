# 11. Opt-in features: Select

Now let's look at one of Telepact's opt-in features: field selection.

## Start the demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Find the `@select_` header

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

```jsonc
{
  "headers.Select_": {
    "@select_": "_ext.Select_"
  },
  "->": {}
}
```

For the full selection rules, let's keep [`doc/extensions.md`](../extensions.md) nearby, especially the `_ext.Select_` section.

## First, request the full result

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 5, "saveResult": {"fn.saveVariable": {"name": "result", "value": 5}}}}]
```

## Now select only `result`

```sh
curl http://localhost:8000/api -X POST --data '[{"@select_": {"->": {"Ok_": ["result"]}}}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 5}}]
```

The value did not change. We just told the server not to send the `saveResult` field.

Next: [12. Binary](./12-binary.md)
