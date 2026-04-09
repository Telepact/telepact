# 15. Stubs

Now let's tell the mock exactly what to return.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the live demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's start the mock server:

```sh
telepact mock --http-url http://localhost:8000/api --port 8001
```

Let's inspect the internal stub function:

```sh
curl -s http://localhost:8001/api \
  --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Relevant excerpt:

```json
{
  "fn.createStub_": {
    "stub": "_ext.Stub_",
    "strictMatch!": "boolean",
    "count!": "integer"
  }
}
```

The full stub shape is described in the [`_ext.Stub_` section of
`extensions.md`](../extensions.md#_extstub_).

Let's create a stub for `fn.add`:

```sh
curl -s http://localhost:8001/api \
  --data '[{}, {"fn.createStub_": {"stub": {"fn.add": {"x": 2, "y": 3}, "->": {"Ok_": {"result": 99}}}}}]'
```

```json
[{}, {"Ok_": {}}]
```

Now the matching call returns our stubbed result:

```sh
curl -s http://localhost:8001/api \
  --data '[{}, {"fn.add": {"x": 2, "y": 3}}]'
```

```json
[{}, {"Ok_": {"result": 99}}]
```

A different argument still falls back to the stock mock behavior:

```sh
curl -s http://localhost:8001/api \
  --data '[{}, {"fn.add": {"x": 2, "y": 4}}]'
```

```json
[{}, {"Ok_": {"result": 0.0014801179065742148}}]
```

And when we're done, we can clear the lifecycle state:

```sh
curl -s http://localhost:8001/api \
  --data '[{}, {"fn.clearStubs_": {}}]'
```

```json
[{}, {"Ok_": {}}]
```

The mock has many more knobs for strictness, randomness, and generation policy.
Those are best explored with `telepact mock --help`, but `fn.createStub_` and
`fn.clearStubs_` are the core lifecycle moves.

Next: [16. Verify](./16-mocking-verify.md)
