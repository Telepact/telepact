# 15. Stock mock

Before we configure anything, let's see what the mock already gives us.

## Start the live demo server

```sh
telepact demo-server --port 8000
```

## Start the mock server

```sh
telepact mock --http-url http://localhost:8000/api --port 8001 --path /api
```

## A malformed request still fails correctly

```sh
curl -s localhost:8001/api -d '[{}, {"fn.add": {"x": "oops", "y": 2}}]'
```

```json
[{}, {"ErrorInvalidRequestBody_": {"cases": [{"path": ["fn.add", "x"], "reason": {"TypeUnexpected": {"actual": {"String": {}}, "expected": {"Number": {}}}}}]}}]
```

That is already powerful: our integration code can prove it is sending
schema-correct requests before it ever talks to the real service.

## A valid request gets a type-correct nonsense result

```sh
curl -s localhost:8001/api -d '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

Example response:

```json
[{}, {"Ok_": {"result": 0.001007557381413671}}]
```

The exact value will vary, but the important part is stable:

- the request is validated
- the response is type compliant

If we need specific values, we'll add stubs next.

Next: [16. Stubs](16-stubs.md)
