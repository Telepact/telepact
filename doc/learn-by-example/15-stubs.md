# 15. Stubs

Now let's teach the mock server exactly what to return for one matching call.

## Start a fresh live server and mock server

In one terminal:

```sh
telepact demo-server --port 8016
```

In another terminal:

```sh
telepact mock --http-url http://127.0.0.1:8016/api --port 8017
```

First, let's confirm the mock exposes a stub API when we ask for internal
schema:

```sh
curl -s http://127.0.0.1:8017/api -X POST -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Schema excerpt:

```json
{
  "fn.createStub_": {
    "stub": "_ext.Stub_",
    "strictMatch!": "boolean",
    "count!": "integer"
  }
}
```

For the shape of `_ext.Stub_`, see the stubs section of the
[Extensions guide](../extensions.md#_extstub_).

Let's install a stub for `fn.add`:

```sh
curl -s http://127.0.0.1:8017/api -X POST -d '[{}, {"fn.createStub_": {"stub": {"fn.add": {"x": 5, "y": 3}, "->": {"Ok_": {"result": 99}}}}}]'
```

```json
[{}, {"Ok_": {}}]
```

Now the matching call returns our chosen value:

```sh
curl -s http://127.0.0.1:8017/api -X POST -d '[{}, {"fn.add": {"x": 5, "y": 3}}]'
```

```json
[{}, {"Ok_": {"result": 99}}]
```

A non-matching call still falls back to normal mock behavior:

```sh
curl -s http://127.0.0.1:8017/api -X POST -d '[{}, {"fn.add": {"x": 5, "y": 4}}]'
```

```json
[{}, {"Ok_": {"result": 0.0014801179065742148}}]
```

And when we want to reset, the lifecycle function is waiting for us:

```sh
curl -s http://127.0.0.1:8017/api -X POST -d '[{}, {"fn.clearStubs_": {}}]'
```

Next: [16. Verify](./16-verify.md)
