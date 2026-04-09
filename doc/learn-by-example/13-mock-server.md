# 13. Mock Server

Let's put a mock server in front of a live Telepact server.

## Start a fresh live server and mock server

In one terminal:

```sh
telepact demo-server --port 8012
```

In another terminal:

```sh
telepact mock --http-url http://127.0.0.1:8012/api --port 8013
```

That mock server pulls the live schema automatically, which makes it a strong
fit for integration work against a real Telepact dependency.

If we ask both servers for the public schema, we get the same API surface:

```sh
curl -s http://127.0.0.1:8012/api -X POST -d '[{}, {"fn.api_": {}}]'
curl -s http://127.0.0.1:8013/api -X POST -d '[{}, {"fn.api_": {}}]'
```

The public schema matches, because the mock absorbed it from the live server.

If we ask the mock for internal definitions, we see much more:

```sh
curl -s http://127.0.0.1:8013/api -X POST -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

That expanded schema includes mock-only tools such as `fn.createStub_` and
`fn.verify_`.

This should be the normal integration pattern for clients:

- either point `telepact mock` directly at the live server
- or cache the schema first with `telepact fetch`, then run `telepact mock --dir`

For example:

```sh
telepact fetch --http-url http://127.0.0.1:8012/api --output-dir ./cached-api
telepact mock --dir ./cached-api --port 8013
```

Next: [14. Stock mock](./14-stock-mock.md)
