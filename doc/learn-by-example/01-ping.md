# 01. Ping

Let's meet the smallest possible Telepact interaction.

## Start a fresh demo server

In one terminal, run:

```sh
telepact demo-server --port 8000
```

In another terminal, call the stock `fn.ping_` function:

```sh
curl -s http://127.0.0.1:8000/api -X POST -d '[{}, {"fn.ping_": {}}]'
```

Response:

```json
[{}, {"Ok_": {}}]
```

## The anatomy of the message

That request is a JSON array with exactly two elements:

1. the **header** object
2. the **body** object

So this request:

```json
[{}, {"fn.ping_": {}}]
```

means:

- header: `{}`
- body: `{ "fn.ping_": {} }`

and this response:

```json
[{}, {"Ok_": {}}]
```

means:

- response headers: `{}`
- response body: `{ "Ok_": {} }`

That two-object message shape is the first Telepact pattern to internalize.

Next: [02. Schema](./02-schema.md)
