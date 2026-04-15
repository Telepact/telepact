# 14. Mock server

Now let's move from "calling a service" to "integrating with a service."

## Start the live demo server

```sh
telepact demo-server --port 8000
```

## Start a mock server from the live schema

In a second terminal:

```sh
telepact mock --http-url http://localhost:8000/api --port 8001 --path /api
```

The mock server absorbs the live server's schema, which makes it a great
integration partner while we are building a client.

## The normal integration pattern

This should be our default habit:

1. point a mock at the live Telepact server
2. develop against the mock first
3. switch to the live service later

If we want a cached local copy of the schema, we can also do this:

```sh
telepact fetch --http-url http://localhost:8000/api --output-dir ./cached-schema
telepact mock --dir ./cached-schema --port 8001 --path /api
```

## Compare the public schema

Live server:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {}}]'
```

Mock server:

```sh
curl -s localhost:8001/api -d '[{}, {"fn.api_": {}}]'
```

Those public schemas match.

If we include internal definitions on the mock, we see more:

```sh
curl -s localhost:8001/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

That extra surface is the mock's control plane.

Next: [15. Stock mock](./15-stock-mock.md)
