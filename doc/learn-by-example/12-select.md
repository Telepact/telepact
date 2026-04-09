# 12. Select

Now let's turn on our first opt-in feature: field selection.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Find the internal `@select_` header

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

The schema entry looks like this:

```json
{
  "headers.Select_": {
    "@select_": "_ext.Select_"
  },
  "->": {}
}
```

For the full rule set, see the [extensions guide](../extensions.md).

## Compare a full response with a selected response

Full response:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 5, "saveResult": {"fn.saveVariable": {"name": "result", "value": 5}}}}]
```

Selected response:

```sh
curl -s localhost:8000/api -d '[{"@select_": {"->": {"Ok_": ["result"]}}}, {"fn.evaluate": {"expression": {"Add": {"left": {"Constant": {"value": 2}}, "right": {"Constant": {"value": 3}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 5}}]
```

Nothing about the function changed. We just told the server which response fields
we wanted back.

Next: [13. Binary](./13-binary.md)
