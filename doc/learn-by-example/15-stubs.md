# 15. Stubs

Let's ask the mock server what it exposes for stubbing:

```sh
curl -s localhost:8080/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]' | python -m json.tool
```

```json
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

For the full stub shape, let's keep
[the `_ext.Stub_` section of `extensions.md`](../extensions.md#_extstub_)
nearby.

Now let's create a stub for `fn.add`.

```sh
curl -s localhost:8080/api -d '[{}, {"fn.createStub_": {"stub": {"fn.add": {"x": 1, "y": 2}, "->": {"Ok_": {"result": 99}}}}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {}
  }
]
```

After that, matching calls return our chosen result:

```sh
curl -s localhost:8080/api -d '[{}, {"fn.add": {"x": 1, "y": 2}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "result": 99
    }
  }
]
```

The mock server also gives us lifecycle helpers such as `fn.clearStubs_`, along
with extra matching and randomness controls that we can explore with the CLI help
later.

Next, let's verify that calls happened when we expected in
[16-verify.md](./16-verify.md).
