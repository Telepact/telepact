# 01. Ping

Let's start with the smallest possible Telepact conversation.

## Start the demo server

In one terminal:

```sh
telepact demo-server --port 8000
```

## Call `fn.ping_`

In another terminal:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.ping_": {}}]'
```

Response:

```json
[{}, {"Ok_": {}}]
```

## The anatomy of a Telepact message

That request was a JSON array with exactly two elements:

```json
[
  {},
  {"fn.ping_": {}}
]
```

- the first object is the **header**
- the second object is the **body**

And the response has the same shape:

```json
[
  {},
  {"Ok_": {}}
]
```

So right away, Telepact gives us a steady mental model:

1. header object
2. body object

We'll keep using that same two-object envelope all the way through the tutorial.

Next: [02. Schema and `fn.add`](./02-schema-and-add.md)
