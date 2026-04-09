# 16. Stubs

Stock mock data is great for shape checking. Stubs are how we ask for specific
results.

## Start the live demo server

```sh
telepact demo-server --port 8000
```

## Start the mock server

```sh
telepact mock --http-url http://localhost:8000/api --port 8001 --path /api
```

## Find `fn.createStub_`

```sh
curl -s localhost:8001/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

The key entry is:

```json
{
  "fn.createStub_": {
    "stub": "_ext.Stub_",
    "strictMatch!": "boolean",
    "count!": "integer"
  }
}
```

For the `_ext.Stub_` shape, see the [extensions guide](../extensions.md).

## Create a stub for `fn.add`

```sh
curl -s localhost:8001/api -d '[{}, {"fn.createStub_": {"stub": {"fn.add": {"x": 1, "y": 2}, "->": {"Ok_": {"result": 99}}}}}]'
```

```json
[{}, {"Ok_": {}}]
```

Now the matching call returns our chosen result:

```sh
curl -s localhost:8001/api -d '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

```json
[{}, {"Ok_": {"result": 99}}]
```

The mock has many more knobs for strictness, randomness, and generation policy.
When we want to reset stubs, the lifecycle function is there too:

```sh
curl -s localhost:8001/api -d '[{}, {"fn.clearStubs_": {}}]'
```

Next: [17. Verify](./17-verify.md)
