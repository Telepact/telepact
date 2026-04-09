# 16. Verify

Stubs change what the mock returns. Verification tells us whether the mock was
called the way we expected.

## Start a fresh live server and mock server

In one terminal:

```sh
telepact demo-server --port 8018
```

In another terminal:

```sh
telepact mock --http-url http://127.0.0.1:8018/api --port 8019
```

Let's first inspect the verification function:

```sh
curl -s http://127.0.0.1:8019/api -X POST -d '[{}, {"fn.api_": {"includeInternal!": true}}]'
```

Schema excerpt:

```json
{
  "fn.verify_": {
    "call": "_ext.Call_",
    "strictMatch!": "boolean",
    "count!": "union.CallCountCriteria_"
  }
}
```

For the `_ext.Call_` rules, see the verification section of the
[Extensions guide](../extensions.md#fnverify_-with-_extcall_).

If we verify too early, the mock correctly tells us nothing has happened yet:

```sh
curl -s http://127.0.0.1:8019/api -X POST -d '[{}, {"fn.verify_": {"call": {"fn.add": {"x": 1, "y": 2}}}}]'
```

```json
[{}, {"ErrorVerificationFailure": {"reason": {"TooFewMatchingCalls": {"wanted": {"AtLeast": {"times": 1}}, "found": 0, "allCalls": []}}}}]
```

Now let's make the call:

```sh
curl -s http://127.0.0.1:8019/api -X POST -d '[{}, {"fn.add": {"x": 1, "y": 2}}]'
```

```json
[{}, {"Ok_": {"result": 0.016654991086877412}}]
```

And verify again:

```sh
curl -s http://127.0.0.1:8019/api -X POST -d '[{}, {"fn.verify_": {"call": {"fn.add": {"x": 1, "y": 2}}}}]'
```

```json
[{}, {"Ok_": {}}]
```

When we want to clear recorded call history, we can use:

```sh
curl -s http://127.0.0.1:8019/api -X POST -d '[{}, {"fn.clearCalls_": {}}]'
```

Next: [17. Auth](./17-auth.md)
