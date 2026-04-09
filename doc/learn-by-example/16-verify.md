# 16. Mocking an integration: Verify

Stubs control outputs. Verification checks whether our client reached out at all.

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

## Find `fn.verify_`

```sh
curl http://localhost:8001/api -X POST --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

```jsonc
{
  "fn.verify_": {
    "call": "_ext.Call_",
    "strictMatch!": "boolean",
    "count!": "union.CallCountCriteria_"
  },
  "->": [
    {
      "Ok_": {}
    },
    {
      "ErrorVerificationFailure": {
        "reason": "union.VerificationFailure_"
      }
    }
  ]
}
```

For the call payload shape, let's keep the `_ext.Call_` section of [`doc/extensions.md`](../extensions.md) nearby.

## Verify before any call happened

```sh
curl http://localhost:8001/api -X POST --data '[{}, {"fn.verify_": {"call": {"fn.add": {"x": 2, "y": 2}}}}]'
```

```json
[{}, {"ErrorVerificationFailure": {"reason": {"TooFewMatchingCalls": {"wanted": {"AtLeast": {"times": 1}}, "found": 0, "allCalls": []}}}}]
```

## Make the call, then verify again

```sh
curl http://localhost:8001/api -X POST --data '[{}, {"fn.add": {"x": 2, "y": 2}}]'
```

```json
[{}, {"Ok_": {"result": 0.016654991086877412}}]
```

```sh
curl http://localhost:8001/api -X POST --data '[{}, {"fn.verify_": {"call": {"fn.add": {"x": 2, "y": 2}}}}]'
```

```json
[{}, {"Ok_": {}}]
```

This is a great way to confirm that our side of the code reached out when we expected it to. And when we want to reset that history, we have `fn.clearCalls_`.

Next: [17. Auth](./17-auth.md)
