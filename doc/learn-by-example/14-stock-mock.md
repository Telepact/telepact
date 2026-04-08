# 14. Stock mock

Before we create any stubs, let's watch the mock server behave on its own.

A malformed request still fails exactly the way a schema-aware integration
should:

```sh
curl -s localhost:8080/api -d '[{}, {"fn.add": {"x": "oops", "y": 2}}]' | python -m json.tool
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

A correct request comes back type-compliant but nonsensical:

```sh
curl -s localhost:8080/api -d '[{}, {"fn.add": {"x": 1, "y": 2}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "result": 0.001007557381413671
    }
  }
]
```

That is the power of a stock Telepact mock. We can prove our client is sending
valid requests and can handle valid result shapes, even before we care about any
particular business value.

If we do need specific values, we can configure them with stubs.

Next, let's create one in [15-stubs.md](./15-stubs.md).
