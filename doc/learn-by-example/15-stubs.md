# 15. Mocking an integration: Stubs

Now let's teach the mock exactly what to return.

## Start the live demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Start the mock server

```sh
cd sdk/cli
uv run telepact mock --http-url http://localhost:8000/api --port 8001
```

## Find `fn.createStub_`

```sh
curl http://localhost:8001/api -X POST --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

```jsonc
{
  "fn.createStub_": {
    "stub": "_ext.Stub_",
    "strictMatch!": "boolean",
    "count!": "integer"
  },
  "->": [
    {
      "Ok_": {}
    }
  ]
}
```

For the stub payload shape, let's keep the `_ext.Stub_` section of [`doc/extensions.md`](../extensions.md) nearby.

## Create a stub for `fn.add`

```sh
curl http://localhost:8001/api -X POST --data '[{}, {"fn.createStub_": {"stub": {"fn.add": {"x": 5, "y": 3}, "->": {"Ok_": {"result": 99}}}}}]'
```

```json
[{}, {"Ok_": {}}]
```

## Call `fn.add`

```sh
curl http://localhost:8001/api -X POST --data '[{}, {"fn.add": {"x": 5, "y": 3}}]'
```

```json
[{}, {"Ok_": {"result": 99}}]
```

When the arguments match, we get the stubbed result back.

The mock has more knobs too: strictness, stub lifetimes, randomness controls, and more. The CLI help covers those. And when we want a clean slate again, we have lifecycle calls such as `fn.clearStubs_`.

Next: [16. Verify](./16-verify.md)
