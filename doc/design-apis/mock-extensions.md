# Mock Extensions

This guide covers Telepact's mock-specific extension types: `_ext.Call_` and
`_ext.Stub_`.

## `_ext.Call_`

`_ext.Call_` represents one call made to a mocked non-internal function.

### Why It Is An Extension

The top-level key must be one concrete function name from the mocked schema, and
the value must validate against that specific function's argument struct. That
is a "choose one key, then switch schema based on that key" rule derived from
the mocked API, not a fixed static union written inline once.

### Shape

```json
{
  "fn.getUser": {
    "id": "user-1"
  }
}
```

Only non-internal mocked functions are valid. Mock control functions such as
`fn.createStub_` are not valid `_ext.Call_` payloads.

### How To Use It

- Pass it to `fn.verify_` to assert that a matching call happened.
- Read it back from verification failures like `allCalls` or
  `additionalUnverifiedCalls`.
- The matching behavior such as strict versus partial matching is controlled by
  the mock API function that consumes the call, not by `_ext.Call_` itself.

### End-To-End Example

Suppose the mocked API contains:

```yaml
- struct.User:
    id: string
    name: string
    admin!: boolean
- fn.getUser:
    id: string
    expand!: boolean
  ->:
    - Ok_:
        user: struct.User
```

Then `_ext.Call_` values look like:

```json
{
  "fn.getUser": {
    "id": "user-1"
  }
}
```

or:

```json
{
  "fn.getUser": {
    "id": "user-1",
    "expand!": true
  }
}
```

You send one of those objects to `fn.verify_`, and Telepact validates the inner
payload against the argument schema for the specific function key you chose.

## `_ext.Stub_`

`_ext.Stub_` represents a mock stub: a call matcher plus the result the mock
server should return.

### Why It Is An Extension

It combines two schema-dependent pieces:

- one concrete non-internal `fn.*` argument payload
- the matching `->` result payload for that same function

That cross-links two dynamic choices from the mocked schema, so it is also not a
single closed `struct.*` definition.

### Shape

```json
{
  "fn.getUser": {
    "id": "user-1"
  },
  "->": {
    "Ok_": {
      "name": "Ada"
    }
  }
}
```

### How To Use It

- Pass it to `fn.createStub_` to install a stub on a mock server.
- The `fn.*` part is the matcher.
- The `->` part must be a valid result payload for that same function.
- Stub lifetime and matching behavior such as `strictMatch!` and `count!` are
  configured on `fn.createStub_`, not inside `_ext.Stub_`.

### End-To-End Example

Using the same mocked `fn.getUser` schema as above, create a stub with:

```json
[
  {},
  {
    "fn.createStub_": {
      "stub": {
        "fn.getUser": {
          "id": "user-1"
        },
        "->": {
          "Ok_": {
            "user": {
              "id": "user-1",
              "name": "Ada"
            }
          }
        }
      }
    }
  }
]
```

The control call succeeds immediately:

```json
[
  {},
  {
    "Ok_": {}
  }
]
```

After that, the mock changes behavior for matching API calls. This request:

```json
[
  {},
  {
    "fn.getUser": {
      "id": "user-1",
      "expand!": true
    }
  }
]
```

returns:

```json
[
  {},
  {
    "Ok_": {
      "user": {
        "id": "user-1",
        "name": "Ada"
      }
    }
  }
]
```

because `fn.createStub_` defaults to partial argument matching. The extra
`expand!` field does not prevent the stub from matching.

A non-matching call still behaves like an unstubbed mock call:

```json
[
  {},
  {
    "fn.getUser": {
      "id": "user-2"
    }
  }
]
```

```json
[
  {},
  {
    "ErrorNoMatchingStub_": {}
  }
]
```

If you need exact argument equality instead, set `strictMatch!` to `true` on
`fn.createStub_`.

## `fn.verify_` With `_ext.Call_`

`fn.verify_` consumes an `_ext.Call_`, not an ordinary free-form object. The
chosen function name determines which argument schema Telepact validates
against, and the call shape you pass affects whether verification succeeds.

Continuing the previous example, suppose the mock has already recorded these two
calls:

```json
[
  {
    "fn.getUser": {
      "id": "user-1",
      "expand!": true
    }
  },
  {
    "fn.getUser": {
      "id": "user-2"
    }
  }
]
```

This verification request succeeds:

```json
[
  {},
  {
    "fn.verify_": {
      "call": {
        "fn.getUser": {
          "id": "user-1"
        }
      }
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

because verification defaults to partial matching and `count!` defaults to
`{"AtLeast": {"times": 1}}`.

The same logical function can fail if you change the verification call:

```json
[
  {},
  {
    "fn.verify_": {
      "call": {
        "fn.getUser": {
          "id": "user-1"
        }
      },
      "strictMatch!": true
    }
  }
]
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
          "allCalls": [
            {
              "fn.getUser": {
                "id": "user-1",
                "expand!": true
              }
            },
            {
              "fn.getUser": {
                "id": "user-2"
              }
            }
          ]
        }
      }
    }
  }
]
```

because exact matching now requires the recorded argument to equal the given
argument exactly.

Changing only `count!` can also change the result:

```json
[
  {},
  {
    "fn.verify_": {
      "call": {
        "fn.getUser": {}
      },
      "count!": {
        "AtMost": {
          "times": 1
        }
      }
    }
  }
]
```

```json
[
  {},
  {
    "ErrorVerificationFailure": {
      "reason": {
        "TooManyMatchingCalls": {
          "wanted": {
            "AtMost": {
              "times": 1
            }
          },
          "found": 2,
          "allCalls": [
            {
              "fn.getUser": {
                "id": "user-1",
                "expand!": true
              }
            },
            {
              "fn.getUser": {
                "id": "user-2"
              }
            }
          ]
        }
      }
    }
  }
]
```

because the empty argument object partially matches both recorded `fn.getUser`
calls.
