# 01. Ping

Let's start with the smallest possible Telepact exchange.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's call the stock `fn.ping_` function:

```sh
curl -s http://localhost:8000/api \
  --data '[{}, {"fn.ping_": {}}]'
```

Response:

```json
[{}, {"Ok_": {}}]
```

This first request already shows us the basic Telepact message shape:

```json
[
  {},
  {
    "fn.ping_": {}
  }
]
```

- the first object is the **header**
- the second object is the **body**
- together they travel as a JSON array with exactly two elements

In this example the header is empty, so all the action is in the body. The body
says which function we want to call, and the response body says which result tag
came back.

That means even the simplest Telepact request is already a complete message:
header first, body second.

Next: [02. Schema](./02-getting-started-schema.md)
