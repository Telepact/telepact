# Extensions

Telepact reserves `_ext.*_` names for internal extension types. These are not
normal schema definitions for API authors to invent freely; they are built-in
placeholders that Telepact libraries interpret with custom validation and
example-generation logic.

## Why Extensions Exist

Normal Telepact definitions are self-describing:

- `struct.*` says exactly which fields are valid.
- `union.*` says exactly which tags and payloads are valid.
- `fn.*` says exactly which argument and result payloads are valid.

Extension types exist for the cases where that is not enough. Their valid JSON
shape depends on surrounding schema context rather than only on the definition
body itself.

That is why internal schemas define these types as empty objects like:

```yaml
_ext.Select_: {}
```

That does not mean "any empty object". It means "Telepact runtime provides the
real validation rules for this reserved type name".

## How Extensions Deviate From Normal Patterns

- Their definitions are placeholders, not full declarative schemas.
- Their valid shape is derived from nearby schema content or the active
  function, not only from the `_ext.*_` entry itself.
- They are implemented by Telepact libraries directly.
- They are intended for internal and mock-control workflows, not as a general
  schema authoring pattern.

If you need ordinary API data modeling, use `struct.*`, `union.*`, `fn.*`,
`headers.*`, and `errors.*`.

## Discovering Them

Call `fn.api_` with `{"includeInternal!": true}` to include internal schemas,
including `_ext.*_` definitions. Add `{"includeExamples!": true}` to get
deterministic example payloads for those types.

The examples below are illustrative request and response messages. They use the
normal Telepact two-object message format:

```json
[
  {
    "@header_": "value"
  },
  {
    "fn.someCall": {}
  }
]
```

## `_ext.Select_`

`_ext.Select_` is the type behind the `@select_` header and any payload field
that wants the same "select fields from a result graph" behavior.

### Why It Is An Extension

The allowed shape is derived from the active function's `Ok_` result payload and
the nested structs and unions reachable from that result. That makes it
context-sensitive in a way that a single static `struct.*` definition cannot
express.

### Shape

`_ext.Select_` is always an object. Its keys are selection targets:

- `->` means "the active function result union".
- `struct.SomeType` means a reachable struct type.
- `union.SomeType` means a reachable union type.

Struct targets map to arrays of allowed field names:

```json
{
  "struct.Profile": ["displayName", "avatarUrl"]
}
```

Union targets map tag names to arrays of allowed field names for that tag:

```json
{
  "union.SearchResult": {
    "User": ["profile"],
    "Team": ["name"]
  }
}
```

The active result union can be selected through `->`:

```json
{
  "->": {
    "Ok_": ["profile", "summary"]
  },
  "struct.Profile": ["displayName"]
}
```

### How To Use It

- Send it in the `@select_` header to trim fields from response payloads.
- You only need to specify the parts you want to narrow; omitted selections
  default to the full reachable shape.
- It applies recursively through arrays and objects when the nested value type
  is a selected struct or union.
- It does not let you omit function argument fields. Selection is for response
  graphs, not for changing request-link shapes.

### End-To-End Example

Suppose the schema contains:

```yaml
- struct.ResultCard:
    title: string
    done!: boolean
- union.ResultItem:
    - Card:
        title: string
    - Note:
        body: string
- fn.selectNested: {}
  ->:
    - Ok_:
        card: struct.ResultCard
        item: union.ResultItem
```

If the server implementation would normally return:

```json
[
  {},
  {
    "Ok_": {
      "card": {
        "title": "Ship docs",
        "done!": false
      },
      "item": {
        "Card": {
          "title": "Ship docs"
        }
      }
    }
  }
]
```

then this request:

```json
[
  {
    "@select_": {
      "->": {
        "Ok_": ["card", "item"]
      },
      "struct.ResultCard": ["title"],
      "union.ResultItem": {
        "Card": []
      }
    }
  },
  {
    "fn.selectNested": {}
  }
]
```

changes the response shape to:

```json
[
  {},
  {
    "Ok_": {
      "card": {
        "title": "Ship docs"
      },
      "item": {
        "Card": {}
      }
    }
  }
]
```

The data values did not change. Only the reachable fields selected by the
header remained in the encoded response.

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

## Practical Guidance

- Prefer ordinary Telepact definitions unless you are intentionally integrating
  with Telepact internal or mock schemas.
- Treat `_ext.*_` types as reserved names with runtime-defined behavior.
- When in doubt, inspect `fn.api_` with internal definitions and examples
  enabled to see the exact shape the current schema exposes.
