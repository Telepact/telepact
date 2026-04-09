# 14. Stock mock

Let's see what a mock gives us before we configure anything.

If we don't already have the published CLI, let's install it:

```sh
uv tool install --prerelease=allow telepact-cli
```

In one terminal, let's start the live demo server:

```sh
telepact demo-server --port 8000
```

In a second terminal, let's start the mock server:

```sh
telepact mock --http-url http://localhost:8000/api --port 8001
```

First, let's send a malformed request to the mock:

```sh
curl -s http://localhost:8001/api \
  --data '[{}, {"fn.add": {"x": "bad", "y": 3}}]'
```

```json
[
  {},
  {
    "ErrorInvalidRequestBody_": {
      "cases": [
        {
          "path": ["fn.add", "x"],
          "reason": {
            "TypeUnexpected": {
              "actual": {"String": {}},
              "expected": {"Number": {}}
            }
          }
        }
      ]
    }
  }
]
```

Now let's send a valid request:

```sh
curl -s http://localhost:8001/api \
  --data '[{}, {"fn.add": {"x": 5, "y": 3}}]'
```

```json
[{}, {"Ok_": {"result": 0.001007557381413671}}]
```

That result is type-compliant but nonsense, and that is exactly the point. The
stock mock helps us verify that our client sends valid requests and can handle
valid response shapes, without waiting for a real backend to implement every
scenario.

If our integration needs specific return values, we can layer in stubs next.

Next: [15. Stubs](./15-mocking-stubs.md)
