# 11. Select

Now let's look at an opt-in feature: field selection.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's inspect the internal header definition:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Relevant excerpt:

```json
{
  "headers.Select_": {
    "@select_": "_ext.Select_"
  },
  "->": {}
}
```

The full selection rules live in the [`_ext.Select_` section of
`extensions.md`](../extensions.md#_extselect_).

Let's make one normal `fn.evaluate` call first:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.saveVariables": {"variables": {"x": 10, "y": 5}}}]'

curl -s http://localhost:8000/api \
  --data '[{}, {"fn.evaluate": {"expression": {"Sub": {"left": {"Variable": {"name": "x"}}, "right": {"Variable": {"name": "y"}}}}}}]'
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

Now let's ask for only the `result` field:

```sh
curl -s http://localhost:8000/api \
  --data '[{"@select_": {"->": {"Ok_": ["result"]}}}, {"fn.evaluate": {"expression": {"Sub": {"left": {"Variable": {"name": "x"}}, "right": {"Variable": {"name": "y"}}}}}}]'
```

```json
[{}, {"Ok_": {"result": 5}}]
```

`saveResult` is gone because we told the server we did not need it. That is the
whole idea of select: the client can trim response fields it already knows it
will ignore.

Next: [12. Binary](./12-opt-in-binary.md)
