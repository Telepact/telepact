# 1 Introduction

The JSON Application Programmer Interface or JAPI ("jay-pee-eye") is an API
expressed and executed with JSON payloads.

# 2 Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119.

The key words "JSON", "string", "number", "boolean", "true", "false", "null",
"object", "member", "value" and "array" in this document are to be interpreted
as described in RFC 8259. In this document, "key" will be used instead of "name"
when discussing JSON objects.

# 3 Design

A JAPI consists of

1. An API description written in JSON using a JAPI-compliant schema that
   describes the various types, functions, and events of the API.
2. JAPI-compliant JSON payloads passed between API providers and consumers that
   represent interactions with the API as described by the API description.
3. An implementation that marshalls the JAPI-compliant JSON payloads from a
   chosen inter-process communication boundary and uses a JAPI-compliant library
   to route JSON payloads to handlers implementing the API description.

```mermaid
  graph TD;
      A-->B;
      A-->C;
      B-->D;
      C-->D;
```

## 3.1 API Description Schema

The API Description Schema describes the various types, functions, and events of
the API.

```json
{
  "struct.{type-name}": {
    "doc": "",
    "fields": {
      "{field-name}": "{type}",
      ...
    }
  },
  ...

  "union.{type-name}": {
    "doc": "",
    "formats": {
      "{format-name}": "{type}",
      ...
    }
  },
  ...

  "enum.{type-name}": {
    "doc": "",
    "values": [
      "{value-name}",
      ...
    ]
  },
  ...

  "error.{error-name}": {
    "doc": "",
    "fields": {
      "{field-name}": "{type}"
      ...
    }
  },
  ...

  "function.{function-name}": {
    "doc": "",
    "input": {
      "{field-name}": "{type}",
      ...
    },
    "output": {
      "{field-name}": "{type}",
      ...
    },
    "errors": [
      "error.{error-name}",
      ...
    ]
  },
  ...

  "event.{type-name}": {
    "doc": "",
    "fields": {
      "{field-name}"
      ...
    }
  }
  ...

}
```

`...` indicates the previous stanza of same indentation can be optionally
repeated.

The keys `"doc"`, `"errors"`, and `"{field-name}"` can be optionally omitted in
every case.

`{*-name}` indicate names that are defined by the API designer and should
satisfy the regular expression `[a-zA-Z][a-zA-Z0-9_]*`. It is recommended that
names for `{type-name}` follow `UpperCamelCase` formatting, `{function-name}`
follow `lower_snake_case` formatting, and `{field-name}`/`{format-name}` follow
`lowerCamelCase` formatting.

`{type}` indicates one of the JAPI types, defined later in this specification.

Example schema:

```json
{
  "enum.Operation": {
    "doc": "A math operation.",
    "values": ["add", "subtract", "multiply", "divide"]
  },

  "union.Value": {
    "doc": "A literal number or name of a variable pointing to saved value.",
    "format": {
      "num": "number",
      "var": "string"
    }
  },

  "struct.Expression": {
    "doc": "A math expression",
    "fields": {
      "x": "union.Value",
      "y": "union.Value",
      "op": "enum.Operation"
    }
  },

  "error.CannotDivideByZero": {
    "doc": "Indicates a computation attempted to divide by zero, which is not allowed.",
    "fields": {
      "message": "string"
    }
  },

  "function.compute": {
    "doc": "Compute a math expression.",
    "input": {
      "expression": "struct.Expression"
    },
    "output": {
      "result": "number"
    }
  },

  "event.ComputationOccurred": {
    "doc": "Indicates to listeners that a computation recently occurred.",
    "fields": {
      "lastResult": "number"
    }
  }
}
```

## 3.2
