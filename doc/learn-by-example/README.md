# Learn Telepact by Example

Let's learn Telepact the same way a client does: by starting a server, sending
small requests, and reading what comes back.

We'll use the CLI demo server for most lessons:

```sh
telepact demo-server --port 8000
```

It serves Telepact at `http://localhost:8000/api`.

When we reach the mocking lessons, we'll also start a mock server in a second
terminal:

```sh
telepact mock --http-url http://localhost:8000/api --port 8080
```

It serves Telepact at `http://localhost:8080/api`.

## A. Getting started

1. [01-ping.md](./01-ping.md)
2. [02-schema.md](./02-schema.md)
3. [03-data-type-validation.md](./03-data-type-validation.md)

## B. Schema

4. [04-scalar-types.md](./04-scalar-types.md)
5. [05-collection-types.md](./05-collection-types.md)
6. [06-structs.md](./06-structs.md)
7. [07-unions.md](./07-unions.md)
8. [08-functions.md](./08-functions.md)
9. [09-service-errors.md](./09-service-errors.md)
10. [10-comments.md](./10-comments.md)

## C. Opt-in features

11. [11-select.md](./11-select.md)
12. [12-binary.md](./12-binary.md)

## D. Mocking an integration

13. [13-mock-server.md](./13-mock-server.md)
14. [14-stock-mock.md](./14-stock-mock.md)
15. [15-stubs.md](./15-stubs.md)
16. [16-verify.md](./16-verify.md)

## E. Auth

17. [17-auth.md](./17-auth.md)

Let's start with the smallest possible call in [01-ping.md](./01-ping.md).
