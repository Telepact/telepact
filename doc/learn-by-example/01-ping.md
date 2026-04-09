# 01. Getting started: Ping

Let's start with the smallest possible Telepact call.

## Start the demo server

In one terminal:

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Call `fn.ping_`

In another terminal:

```sh
curl http://localhost:8000/api -X POST --data '[{}, {"fn.ping_": {}}]'
```

```json
[{}, {"Ok_": {}}]
```

## Read the message shape

A Telepact message is always a JSON array with two elements:

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

Here the header is empty, and the body says, “let's call `fn.ping_` with an empty argument object.”

The response uses the same shape:

```json
[
  {},
  {
    "Ok_": {}
  }
]
```

That means Telepact keeps one wire pattern for both requests and responses.

Next: [02. Schema](./02-schema.md)
