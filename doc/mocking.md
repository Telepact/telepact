# Mocking

Telepact mock servers expose a control API alongside the mocked application
schema. The main control functions are `fn.createStub_`, `fn.verify_`, and
`fn.verifyNoMoreInteractions_`.

The `_ext.Stub_` and `_ext.Call_` helper types are intentionally open because
their shape depends on the functions present in the mocked schema. In practice:

- `_ext.Stub_` is an object with exactly one `fn.*` call payload and a `->`
  result payload.
- `_ext.Call_` is an object with exactly one `fn.*` call payload.

## `fn.createStub_`

Creates a stubbed response for a matching function call.

```json
[
  {},
  {
    "fn.createStub_": {
      "stub": {
        "fn.someFunction": {
          "arg": "value"
        },
        "->": {
          "Ok_": {
            "result": 1
          }
        }
      },
      "strictMatch!": true,
      "count!": 1
    }
  }
]
```

## `fn.verify_`

Checks that a matching call happened.

```json
[
  {},
  {
    "fn.verify_": {
      "call": {
        "fn.someFunction": {
          "arg": "value"
        }
      },
      "strictMatch!": true,
      "count!": {
        "Exact": {
          "times": 1
        }
      }
    }
  }
]
```

## `fn.verifyNoMoreInteractions_`

Checks that there are no additional unverified calls.

```json
[
  {},
  {
    "fn.verifyNoMoreInteractions_": {}
  }
]
```

## Matching Controls

- `strictMatch! = true` means the request must match exactly.
- Omitting `strictMatch!` allows partial matching semantics where supported by
  the mock server.
- `count!` on `fn.createStub_` limits how many times a stub may be consumed.
- `count!` on `fn.verify_` accepts `Exact`, `AtLeast`, or `AtMost`.

## Discoverability

If you call `fn.api_` on a mock server with `{"includeInternal!": true}`, the
response will include the mock control schema definitions. If you also pass
`{"includeExamples!": true}`, Telepact will attach deterministic example
payloads to those entries.
