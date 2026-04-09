# 17. Verify

Sometimes we do not need to control the response. We just need to prove that our
client made a call.

## Start the live demo server

```sh
telepact demo-server --port 8000
```

## Start the mock server

```sh
telepact mock --http-url http://localhost:8000/api --port 8001 --path /api
```

## Find `fn.verify_`

```sh
curl -s localhost:8001/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

The entry looks like this:

```json
{
  "fn.verify_": {
    "call": "_ext.Call_",
    "strictMatch!": "boolean",
    "count!": "union.CallCountCriteria_"
  }
}
```

For the `_ext.Call_` shape, see the [extensions guide](../extensions.md).

## Verify before the call

Let's clear any old history first:

```sh
curl -s localhost:8001/api -d '[{}, {"fn.clearCalls_": {}}]'
curl -s localhost:8001/api -d '[{}, {"fn.verify_": {"call": {"fn.add": {"x": 7, "y": 8}}}}]'
```

Response:

```json
[{}, {"ErrorVerificationFailure": {"reason": {"TooFewMatchingCalls": {"wanted": {"AtLeast": {"times": 1}}, "found": 0, "allCalls": []}}}}]
```

## Verify after the call

```sh
curl -s localhost:8001/api -d '[{}, {"fn.add": {"x": 7, "y": 8}}]'
curl -s localhost:8001/api -d '[{}, {"fn.verify_": {"call": {"fn.add": {"x": 7, "y": 8}}}}]'
```

Response:

```json
[{}, {"Ok_": {}}]
```

So `fn.verify_` is our way to confirm that our side of the integration reached
out when we expected it to.

Next: [18. Auth](./18-auth.md)
