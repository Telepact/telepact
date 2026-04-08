# 16. Verify

The mock can also record calls and let us verify that our client reached out at
the right time.

The internal schema shows that with `fn.verify_`:

```sh
curl -s localhost:8080/api -d '[{}, {"fn.api_": {"includeInternal!": true}}]' | python -m json.tool
```

```json
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

For the call shape, let's keep
[the `_ext.Call_` section of `extensions.md`](../extensions.md#_extcall_)
nearby.

First let's clear any earlier history and verify too early:

```sh
curl -s localhost:8080/api -d '[{}, {"fn.clearCalls_": {}}]' > /dev/null
curl -s localhost:8080/api -d '[{}, {"fn.verify_": {"call": {"fn.add": {"x": 1, "y": 2}}}}]' | python -m json.tool
```

```json
[
  {},
  {
    "ErrorVerificationFailure": {
      "reason": {
        "TooFewMatchingCalls": {
          "wanted": {
            "AtLeast": {
              "times": 1
            }
          },
          "found": 0,
          "allCalls": []
        }
      }
    }
  }
]
```

Now let's make the call and verify again:

```sh
curl -s localhost:8080/api -d '[{}, {"fn.add": {"x": 1, "y": 2}}]' | python -m json.tool
curl -s localhost:8080/api -d '[{}, {"fn.verify_": {"call": {"fn.add": {"x": 1, "y": 2}}}}]' | python -m json.tool
```

```json
[
  {},
  {
    "Ok_": {
      "result": 99
    }
  }
]
```

```json
[
  {},
  {
    "Ok_": {}
  }
]
```

This is great for proving that our code really did call the integration point we
expected. And when we want to reset history, `fn.clearCalls_` is there for the
full lifecycle.

Next, let's close the walkthrough with auth in [17-auth.md](./17-auth.md).
