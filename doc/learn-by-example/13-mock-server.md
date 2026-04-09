# 13. Mocking an integration: Mock server

Let's put a mock server in front of a live Telepact service.

## Start the live demo server

In one terminal:

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Start the mock server from the live schema

In a second terminal:

```sh
cd sdk/cli
uv run telepact mock --http-url http://localhost:8000/api --port 8001
```

The mock absorbs the live schema automatically.

That makes it a great default integration pattern: point client code at a mock first. For repeatable local work, we can also cache the real schema with `telepact fetch` and then start `telepact mock --dir ...` from that saved schema.

## Check that the public schema matches

Live server:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.api_": {}}]'
```

Mock server:

```sh
curl http://localhost:8001/api -X POST --data '[{}, {"fn.api_": {}}]'
```

Both responses include the same public entries, such as:

```jsonc
{
  "fn.add": {
    "x": "number",
    "y": "number"
  },
  "->": [
    {
      "Ok_": {
        "result": "number"
      }
    }
  ]
}
```

## Now ask the mock for its internal schema

```sh
curl http://localhost:8001/api -X POST --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Now we see extra mock-control tools like `fn.createStub_`, `fn.verify_`, `fn.clearStubs_`, and `fn.clearCalls_`.

Next: [14. Stock mock](./14-stock-mock.md)
