# 14. Stock Mock

Let's see what we get from a mock server before adding any stubs.

## Start a fresh live server and mock server

In one terminal:

```sh
telepact demo-server --port 8014
```

In another terminal:

```sh
telepact mock --http-url http://127.0.0.1:8014/api --port 8015
```

First, let's send malformed input to the mock:

```sh
curl -s http://127.0.0.1:8015/api -X POST -d '[{}, {"fn.add": {"x": "oops"}}]'
```

```json
[{}, {"ErrorInvalidRequestBody_": {"cases": [{"path": ["fn.add"], "reason": {"RequiredObjectKeyMissing": {"key": "y"}}}, {"path": ["fn.add", "x"], "reason": {"TypeUnexpected": {"actual": {"String": {}}, "expected": {"Number": {}}}}}]}}]
```

Now let's send a valid request:

```sh
curl -s http://127.0.0.1:8015/api -X POST -d '[{}, {"fn.add": {"x": 5, "y": 3}}]'
```

```json
[{}, {"Ok_": {"result": 0.001007557381413671}}]
```

That number is nonsense from the business point of view, but it is perfectly
schema-compliant. That is the power of the stock mock: it lets us verify our
client is sending valid calls and can handle valid return shapes before we ever
point at the real service.

If we need specific returned values, stubs are the next step.

Next: [15. Stubs](./15-stubs.md)
