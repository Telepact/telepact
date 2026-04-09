# 16. Verify

Stubs control return values. Verification answers a different question: did our
client make the call we expected?

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

Let's inspect the verification function:

```sh
curl -s http://localhost:8001/api \
  --data '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Relevant excerpt:

```json
{
  "fn.verify_": {
    "call": "_ext.Call_",
    "strictMatch!": "boolean",
    "count!": "union.CallCountCriteria_"
  }
}
```

The full call shape is described in the [`_ext.Call_` section of
`extensions.md`](../extensions.md#_extcall_).

Let's clear any old call history first:

```sh
curl -s http://localhost:8001/api \
  --data '[{}, {"fn.clearCalls_": {}}]'
```

Now let's verify a call before it has happened:

```sh
curl -s http://localhost:8001/api \
  --data '[{}, {"fn.verify_": {"call": {"fn.add": {"x": 123, "y": 456}}}}]'
```

```json
[
  {},
  {
    "ErrorVerificationFailure": {
      "reason": {
        "TooFewMatchingCalls": {
          "wanted": {"AtLeast": {"times": 1}},
          "found": 0,
          "allCalls": []
        }
      }
    }
  }
]
```

Now let's make the call, then verify again:

```sh
curl -s http://localhost:8001/api \
  --data '[{}, {"fn.add": {"x": 123, "y": 456}}]'

curl -s http://localhost:8001/api \
  --data '[{}, {"fn.verify_": {"call": {"fn.add": {"x": 123, "y": 456}}}}]'
```

```json
[{}, {"Ok_": {}}]
```

That gives us a clean way to assert that our side of the integration really did
reach out when it was supposed to. And just like stubs, calls have lifecycle
helpers too, including `fn.clearCalls_`.

Next: [17. Auth](./17-auth.md)
