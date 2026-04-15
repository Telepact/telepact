# 10. Headers

Headers are shaped a bit like structs, but they play by different rules.

## Start the demo server

```sh
telepact demo-server --port 8000
```

## Look at internal header definitions

```sh
curl -s localhost:8000/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

For example:

```json
{
  "headers.Id_": {
    "@id_": "any"
  },
  "->": {
    "@id_": "any"
  }
}
```

Headers differ from structs in two important ways:

1. every defined header field is already optional
2. undefined header fields are still allowed

That is why header names use `@` and do not use `!`.

## A real example with `@id_`

```sh
curl -s localhost:8000/api -d '[{"@id_": "lesson-10"}, {"fn.add": {"x": 1, "y": 2}}]'
```

Response:

```json
[{"@id_": "lesson-10"}, {"Ok_": {"result": 3}}]
```

So `@id_` is just a correlation helper: the server reflects it back.

Next: [11. Comments](11-comments.md)
