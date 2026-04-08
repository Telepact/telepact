# 01. Ping

Let's start by proving that a Telepact server is alive.

In one terminal, start the demo server:

```sh
telepact demo-server --port 8000
```

In another terminal, send the smallest useful Telepact request:

```sh
curl -s localhost:8000/api -d '[{}, {"fn.ping_": {}}]'
```

```json
[{}, {"Ok_": {}}]
```

That request teaches us the core message shape right away:

```json
[header, body]
```

In our request:

- the first object is the header, and it is empty: `{}`
- the second object is the body
- the body contains exactly one top-level key: `fn.ping_`

In the response:

- the header is empty again
- the body contains exactly one result tag: `Ok_`

So even this tiny round trip already shows the full Telepact rhythm: send one
message, get one message back, and always read both the header object and the
body object.

Next, let's ask the server to describe itself in
[02-schema.md](./02-schema.md).
