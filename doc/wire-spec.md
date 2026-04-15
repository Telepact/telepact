# Telepact Wire Specification

This document specifies Telepact on the wire: the serialized message shape,
reserved wire headers, binary negotiation, and the standard error forms that a
conforming implementation exchanges with another conforming implementation.

This document is intentionally transport-agnostic. Telepact defines request and
response bytes, not URL structure, sockets, topics, framing, or status codes.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
this document are to be interpreted as described in RFC 2119 and RFC 8174.

## 1. Transport model

A Telepact interaction is one request message and one response message.

The surrounding transport:

- MUST preserve request and response bytes exactly
- MAY use HTTP, WebSocket messages, queues, stdio, or any other byte transport
- MAY attach transport-specific metadata, but that metadata is outside the
  Telepact message

## 2. Message envelope

A Telepact message MUST be a two-element array:

```json
[headers, body]
```

Rules:

- `headers` MUST be an object
- `body` MUST be an object
- `body` MUST contain exactly one member
- the single body value MUST be an object

A request body target is normally a function name:

```json
[{}, {"fn.example": {"field": 1}}]
```

A response body target is normally a result tag:

```json
[{}, {"Ok_": {"field": 1}}]
```

Body targets are schema-coupled:

- a request target MUST name one function
- a response target MUST be one tag from that function's result union
- `Ok_` is the success tag
- other response tags are error outcomes

## 3. Header and body naming rules

The body carries domain data. Headers carry metadata and protocol control
signals.

### 3.1 Body fields

Telepact preserves schema field names on the wire.

That includes optional struct fields with the `!` suffix:

```json
{"displayName!": "Ada"}
```

### 3.2 Header fields

Telepact header names begin with `@`.

Header definitions are open-world:

- declared header names are type-checked
- undeclared header names are still allowed
- header names do not use the `!` suffix because headers are implicitly optional

## 4. JSON encoding

The JSON form of a Telepact message MUST be encoded as UTF-8 JSON text whose
parsed value is the two-element Telepact array.

Example:

```json
[
  {
    "@id_": "req-7"
  },
  {
    "fn.add": {
      "x": 1,
      "y": 2
    }
  }
]
```

### 4.1 Bytes in JSON

Telepact supports a `bytes` scalar type even though JSON has no native bytes
value.

When a JSON message carries a `bytes` value, the actual value on the wire MUST
be a Base64 string.

For requests, schema context alone identifies which fields are `bytes`.

For responses, the message headers MUST include `@base64_` describing which
response paths are Base64-encoded.

Example:

```json
[
  {
    "@base64_": {
      "Ok_": {
        "blob": true
      }
    }
  },
  {
    "Ok_": {
      "blob": "AAEC"
    }
  }
]
```

The `@base64_` value is a path tree:

- object keys step through object fields or union tags
- `"*"` steps through every element of an array or every value of an object map
- `true` marks a leaf that is Base64-encoded bytes

Example for nested bytes:

```json
{
  "@base64_": {
    "Ok_": {
      "items": {
        "*": {
          "payload": true
        }
      }
    }
  }
}
```

## 5. Standard request and response errors

A conforming implementation MUST support the standard parse and validation error
shapes.

### 5.1 Parse failure response

If request bytes cannot be decoded into a Telepact message, the response body
MUST be:

```json
{
  "ErrorParseFailure_": {
    "reasons": [
      {
        "JsonInvalid": {}
      }
    ]
  }
}
```

Standard parse failure reasons are:

- `IncompatibleBinaryEncoding`
- `BinaryDecodeFailure`
- `JsonInvalid`
- `ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject`
- `ExpectedJsonArrayOfTwoObjects`

### 5.2 Validation failure response

Schema-level request and response failures use a `cases` array of validation
failures:

```json
{
  "ErrorInvalidRequestBody_": {
    "cases": [
      {
        "path": ["fn.add", "z"],
        "reason": {
          "ObjectKeyDisallowed": {}
        }
      }
    ]
  }
}
```

A validation failure object has this shape:

```json
{
  "path": ["..."],
  "reason": {"SomeReason": {}}
}
```

Standard validation error tags are:

- `ErrorInvalidRequestHeaders_`
- `ErrorInvalidRequestBody_`
- `ErrorInvalidResponseHeaders_`
- `ErrorInvalidResponseBody_`
- `ErrorUnknown_`

Standard validation reasons include:

- `TypeUnexpected`
- `NullDisallowed`
- `ObjectKeyDisallowed`
- `RequiredObjectKeyPrefixMissing`
- `ArrayElementDisallowed`
- `NumberOutOfRange`
- `ObjectSizeUnexpected`
- `ExtensionValidationFailed`
- `ObjectKeyRegexMatchCountUnexpected`
- `RequiredObjectKeyMissing`
- `FunctionUnknown`

## 6. Reserved wire headers

This section describes the reserved headers that affect Telepact on the wire.

### 6.1 `@id_`

`@id_` is a correlation identifier.

- a request MAY include `@id_`
- if present, the response MUST reflect the same value unchanged

### 6.2 `@time_`

`@time_` is an integer timeout hint supplied by the requester.

It communicates caller intent but does not define transport timeout behavior.

### 6.3 `@unsafe_`

`@unsafe_` is a boolean request flag:

```json
{"@unsafe_": true}
```

If `true`, it requests that the responder skip response validation before
serializing the response.

### 6.4 `@select_`

`@select_` applies response shaping to the response graph.

Its value is the reserved `_ext.Select_` structure:

- `"->"` targets the active result union
- `"struct.SomeType"` targets a reachable struct
- `"union.SomeType"` targets a reachable union

Example:

```json
{
  "@select_": {
    "->": {"Ok_": ["profile"]},
    "struct.Profile": ["displayName"]
  }
}
```

### 6.5 `@auth_`

If the schema defines `union.Auth_`, `@auth_` is the conventional location for
credentials.

### 6.6 `@warn_`

`@warn_` is a response header containing warning values.

### 6.7 `@base64_`

`@base64_` is a response header that marks JSON response paths whose wire values
are Base64 strings representing `bytes` values.

### 6.8 `@bin_`, `@enc_`, and `@pac_`

These headers control Telepact binary negotiation.

They are defined in the next section.

## 7. Binary negotiation

Telepact binary is runtime-negotiated. The schema does not carry manually
assigned field ids.

### 7.1 Overview

A requester opts into binary negotiation by sending `@bin_`.

- `@bin_` MUST be an array of integer checksums
- `[]` means "I want binary, but I do not yet know an encoding"
- the first checksum identifies the encoding used by a binary request body

Example handshake request:

```json
[
  {
    "@bin_": []
  },
  {
    "fn.getPaperTape": {}
  }
]
```

If the responder can produce a successful `Ok_` result, it replies with:

- `@bin_`: the checksum it chose
- `@enc_`: the field-id map if the requester did not already advertise that
  checksum
- optionally `@pac_`: `true` if packed binary was requested and used

### 7.2 Binary field-id map

`@enc_` is an object mapping string keys to integer field ids.

Example:

```json
{
  "@bin_": [1059755324],
  "@enc_": {
    "Ok_": 0,
    "api": 1,
    "data": 2,
    "fn.api_": 3
  }
}
```

The field-id map MUST be derived as follows:

1. collect every function name
2. collect every field reachable from every function argument graph
3. collect `Ok_`
4. collect every field and nested tag reachable from every `Ok_` response graph
5. sort all collected keys lexicographically
6. assign ids `0..n-1` in that sorted order
7. compute the checksum as the CRC32 of the newline-joined sorted keys

Only request graphs and successful `Ok_` response graphs participate in this
map. Error tags are not part of the binary body encoding.

### 7.3 MessagePack form

The binary form of a Telepact message MUST be a MessagePack encoding of the same
logical two-element array:

```text
[headers, body]
```

In binary form:

- `headers` remain a normal string-keyed object
- body keys are replaced by integer field ids from the negotiated map
- `bytes` values use native MessagePack binary values rather than Base64 strings

Logical example:

```text
[
  {"@bin_": [1059755324]},
  {0: {1: []}}
]
```

### 7.4 Binary request rules

A binary request body:

- MUST use the first checksum in `@bin_`
- MUST use integer field ids from the matching `@enc_` map
- MAY include `@pac_`: `true` to request packed list encoding

If the checksum does not match the responder's current checksum, the responder
MUST reject the binary request with `ErrorParseFailure_` using the reason
`IncompatibleBinaryEncoding`.

If a binary field id cannot be mapped back to a string key, the responder MUST
reject the binary request with `ErrorParseFailure_` using the reason
`BinaryDecodeFailure`.

### 7.5 Binary response rules

Only successful `Ok_` responses participate in binary body encoding.

Therefore:

- an `Ok_` response to a binary-enabled request MAY be sent as MessagePack
- an error response MUST be sent in normal JSON Telepact form
- because errors are JSON, their body target remains a string tag such as
  `"ErrorInvalidRequestBody_"`

## 8. Packed list encoding

If `@pac_` is `true`, an implementation MAY replace eligible arrays of objects in
MessagePack bodies with a packed row form.

This document reserves two MessagePack extension codes:

- extension code `17`: packed-list marker
- extension code `18`: undefined-slot marker

### 8.1 Packed list shape

A packed list has this logical shape:

```text
[
  ext(17),
  header,
  row1,
  row2,
  ...
]
```

Where:

- `header` is an array beginning with `null`
- each later header entry is either:
  - an integer field id, or
  - a nested header array whose first element is the parent field id
- each row is a positional array aligned to the header columns
- a missing value in a row is represented by `ext(18)`

Example logical shape:

```text
[
  ext(17),
  [null, 6, 9],
  [1, "one"],
  [2, "two"]
]
```

Which corresponds to the unpacked logical value:

```text
[
  {6: 1, 9: "one"},
  {6: 2, 9: "two"}
]
```

Nested objects are represented by nested headers.

## 9. Interaction rules

A conforming Telepact exchange therefore follows this sequence:

1. send one Telepact request message
2. parse it as JSON or MessagePack
3. validate headers and body against the schema and reserved protocol rules
4. produce exactly one Telepact response message
5. serialize that response as JSON, or as MessagePack only for successful binary
   `Ok_` responses

## 10. Minimal examples

### 10.1 Plain JSON request and response

```json
[
  {},
  {
    "fn.helloWorld": {}
  }
]
```

```json
[
  {},
  {
    "Ok_": {
      "msg": "Hello world!"
    }
  }
]
```

### 10.2 Invalid request body

```json
[
  {},
  {
    "fn.add": {
      "x": 1,
      "z": 2
    }
  }
]
```

```json
[
  {},
  {
    "ErrorInvalidRequestBody_": {
      "cases": [
        {
          "path": ["fn.add", "z"],
          "reason": {"ObjectKeyDisallowed": {}}
        },
        {
          "path": ["fn.add"],
          "reason": {"RequiredObjectKeyMissing": {"key": "y"}}
        }
      ]
    }
  }
]
```

### 10.3 Binary handshake

Handshake request:

```json
[
  {
    "@bin_": []
  },
  {
    "fn.ping_": {}
  }
]
```

Logical MessagePack response content:

```text
[
  {
    "@bin_": [1059755324],
    "@enc_": {
      "Ok_": 0,
      "fn.ping_": 5
    }
  },
  {
    0: {}
  }
]
```
