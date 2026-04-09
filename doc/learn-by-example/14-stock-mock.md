# 14. Mocking an integration: Stock mock

Let's see what the mock gives us before we configure anything.

## Start the live demo server

```sh
cd sdk/cli
uv run telepact demo-server --port 8000
```

## Start the mock server

```sh
cd sdk/cli
uv run telepact mock --http-url http://localhost:8000/api --port 8001
```

## Send a malformed request

```sh
curl http://localhost:8001/api -X POST --data '[{}, {"fn.add": {"x": "oops", "y": 3}}]'
```

```json
[{}, {"ErrorInvalidRequestBody_": {"cases": [{"path": ["fn.add", "x"], "reason": {"TypeUnexpected": {"actual": {"String": {}}, "expected": {"Number": {}}}}}]}}]
```

That is exactly what we want from an integration mock: it still validates our request shape.

## Send a valid request

```sh
curl http://localhost:8001/api -X POST --data '[{}, {"fn.add": {"x": 5, "y": 3}}]'
```

```json
[{}, {"Ok_": {"result": 0.001007557381413671}}]
```

The result is nonsense, but it is type-compliant nonsense.

That is the power of the stock mock. We can keep tightening our client until requests validate and responses are handled correctly, even before we care about specific business values.

If we *do* need specific values back, let's stub them next.

Next: [15. Stubs](./15-stubs.md)
