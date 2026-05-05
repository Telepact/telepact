# `_ext.Select_`

`_ext.Select_` is the type behind the `.select_` header and any payload field
that wants the same "select fields from a result graph" behavior.

## Why It Is An Extension

The allowed shape is derived from the active function's `Ok_` result payload and
the nested structs and unions reachable from that result. That makes it
context-sensitive in a way that a single static `struct.*` definition cannot
express.

## Shape

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

## How To Use It

- Send it in the `.select_` header to trim fields from response payloads.
- You only need to specify the parts you want to narrow; omitted selections
  default to the full reachable shape.
- It applies recursively through arrays and objects when the nested value type
  is a selected struct or union.
- It does not let you omit function argument fields. Selection is for response
  graphs, not for changing request-link shapes.

## End-To-End Example

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
    ".select_": {
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

For a runnable minimal version of this pattern, see
[`example/py-select`](../../example/py-select/README.md).
