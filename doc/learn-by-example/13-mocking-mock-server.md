# 13. Mock server

Let's move from learning a service to integrating with one.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the live demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's start a mock server that points at it:

```sh
telepact mock --http-url http://localhost:8000/api --port 8001
```

Now the mock absorbs the live schema and can simulate that integration surface.
That is the normal Telepact pattern for clients: integrate against a mock,
either by pointing at a live Telepact server directly, or by first caching its
schema with `telepact fetch` and then mocking from the local schema.

Let's confirm the public schema matches the live server:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.api_": {}}]'

curl -s http://localhost:8001/api \
  --data '[{}, {"fn.api_": {}}]'
```

In this version of the demo, both responses expose the same 19 public schema
entries.

If we include internal definitions on the mock, we see a lot more mock-specific
machinery than we saw on the live server:

```sh
curl -s http://localhost:8001/api \
  --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Examples of extra mock entries:

```json
[
  {"fn.createStub_": {"stub": "_ext.Stub_", ...}},
  {"fn.verify_": {"call": "_ext.Call_", ...}},
  {"fn.clearStubs_": {}},
  {"fn.clearCalls_": {}},
  ...
]
```

So the mock is not just a passive mirror. It mirrors the target API and adds a
full mock-control surface on top.

Next: [14. Stock mock](./14-mocking-stock-mock.md)
