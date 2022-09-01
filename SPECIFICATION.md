# 1 Introduction

The JSON Application Programming Interface or JAPI ("jay-pee-eye") is an API
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

A JAPI consists of the following:

1. An API description written in JSON using a JAPI-compliant schema that
   describes the various types, functions, and events of the API.
2. JAPI-compliant JSON payloads passed between API providers and consumers that
   represent interactions with the API as defined by the API description.
3. An API implementation on the API provider that uses a JAPI-compliant library
   to marshall JAPI-compliant JSON payloads from/to a chosen inter-process
   communication boundary to/from handlers in the API provider code.

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

  "event.{event-name}": {
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
names for `{type-name}`/`{event-name}`/`{error-name}` follow `UpperCamelCase`
formatting, `{function-name}` follow `lower_snake_case` formatting, and
`{field-name}`/`{format-name}` follow `lowerCamelCase` formatting.

`{type}` indicates one of the JAPI types, defined later in this specification.

Example schema:

```json
{
  "enum.Operation": {
    "doc": "A math operation.",
    "values": ["add", "subtract", "multiply", "divide"]
  },

  "union.Value": {
    "doc": "A literal number or name of a variable stored in memory.",
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

  "error.No": {
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
    },
    "error.CannotDivideByZero": {}
  },

  "function.store": {
    "doc": "Store a variable in memory. Overwrites any existing variables.",
    "input": {
      "name": "string",
      "value": "number"
    },
    "output": {}
  },

  "event.NewVariableStored": {
    "doc": "Indicates a new variable was stored in memory.",
    "fields": {
      "name": "string"
    }
  }
}
```

## 3.2 JSON Payloads

JSON payloads in JAPI indicate interactions with the API, such as function
calls, function returns, or events.

### 3.2.1 Basic format

All JSON payloads in JAPI follow the same general format, a JSON array with 3
elements, a string indicating the payload type, an object containing headers,
and an object containing the primary body of data.

```json
[
  "{payload-type}",
  {
    "{header-key}": "{header-value}",
    ...
  },
  {
    "{body-key}": "{body-value}"
    ...
  }
]
```

`...` indicates the previous stanza of same indentation can be optionally
repeated.

`{payload-type}` is a reference to a top-level definition in the API
description, and it establishes the format of the payload body.

`{header-key}` and `{header-value}` are used to include headers in a JSON
payload to increase expressivity when interacting with a JAPI. All instances of
`{header-key}` are optional and not required for all payload types.

`{body-key}` and `{body-value}` make up the primary body of a JAPI JSON payload.
The specific values allowed for these placeholders is determined by the payload
type.

### 3.2.2 Function Calls

```json
[
  "function.{function-name}",
  {
    "{header-key}": "{header-value}",
    ...
  },
  {
    "{body-key}": "{body-value}"
    ...
  }
]
```

Example:

```json
[
  "function.compute",
  {},
  {
    "expression": {
      "x": 1,
      "y": 2,
      "op": "add"
    }
  }
]
```

### 3.2.3 Function Returns

```json
[
  "function.{function-name}.output",
  {
    "{header-key}": "{header-value}",
    ...
  },
  {
    "{body-key}": "{body-value}"
    ...
  }
]
```

Example:

```json
[
  "function.compute.output",
  {},
  {
    "result": 3
  }
]
```

### 3.2.3.1 Function Returns with error

```json
[
  "error.{error-name}",
  {
    "{header-key}": "{header-value}",
    ...
  },
  {
    "{body-key}": "{body-value}"
    ...
  }
]
```

Example:

```json
[
  "error.CannotDivideByZero",
  {},
  {
    "message": "Dividing by zero is not allowed."
  }
]
```

### 3.2.4 Events

```json
[
  "event.{type-name}",
  {
    "{header-key}": "{header-value}",
    ...
  },
  {
    "{body-key}": "{body-value}"
    ...
  }
]
```

Example:

```json
[
  "event.ComputationSuccessful",
  {},
  {
    "lastSuccessfulResult": 3
  }
]
```

## 3.3 Provider API Implementation

The rules and execution of a JAPI are driven entirely by the implementation of
the API provider. This implementation is responsible for moving JAPI payloads
from/to the API provider's chosen inter-process communication (IPC) boundary
to/from a JAPI-compliant processing library that will inspect the payload and
route it to a proper handler in the API provider code.

### 3.3.1 Function Calls

For JAPIs offering functions, the JAPI provider implementation MUST set up a
transport that allows for both receiving and returning JSON payloads to and from
an API consumer. The full interaction will consist of the following:

1. the sending of a JAPI Function Input JSON payload from a consumer that is
   received by the provider implementation through it's chosen IPC boundary,
2. the passing of that JSON payload to a JAPI processor for parsing and
   validation
3. the passing of the deserialized data from the function input payload to API
   implementation handlers to perform a function call,
4. the returning of the result of that function call back to the JAPI processor
   for validation and serialization into a JAPI Function Output JSON payload,
5. the sending of the JAPI Function Output JSON payload from the provider
   through the IPC boundary back the consumer

HTTP Example:

```java
import io.javalin.Javalin;
import io.github.brenbar.japi.JapiProcessor;

public class Main {

    private static Map<String, Number> storedVariables = new HashMap<String, Number>();

    public static void main(String[] args) {
        var japiProcessor = new JapiProcessor(Main::handle);
        var app = Javalin.create().start(8080);
        app.get("/api/v1", ctx -> {
            // 1. Receive a JAPI Function Input JSON payload sent from its API consumer from HTTP request.
            String inputJson = ctx.body();

            // 2. Pass the received JSON payload to a JAPI processor, which
            //    will parse the JSON payload into data objects the API implementation
            //    can use for function calls.
            String outputJson = japiProcessor.process(inputJson);

            // 5. Send JAPI Function Output JSON payload to consumer with HTTP response body.
            ctx.result(outputJson);
        });
    }

    private static Map<String, Object> handle(String functionName, Map<String, Object> headers, Map<String, Object> input) {
        // 3. Use deserialized JAPI Function Input to start function call
        Map<String, Object> result = switch (functionName) {
            case "compute" -> {
                var x = getValue(input.get("x"));
                var y = getValue(input.get("y"));
                var op = input.get("op");
                var result = switch (op) {
                    case "add" -> x + y
                    case "sub" -> x - y
                    case "mul" -> x * y
                    case "div" ->
                }
                yield Map.of("result", input.get("x") + input.get("y"));
            }
            default -> throw new RuntimeException("Function %s not found".formatted(functionName))
        };

        // 4. Return function result back the JapiProcessor for validation against the JAPI description,
        //    and then serialization into a JAPI Function Output payload.
        return result;
    }

    private static double getValue(Map<String, Object> value) {
        var entry = value.entrySet().iterator().next();
        var format = entry.getKey();
        var value = entry.getValue();
        return switch (format) {
            case "var" -> storedVariables.get(value).doubleValue();
            case "num" -> value.doubleValue();
            default -> throw new RuntimeException()
        };
    }
}
```

Websocket Example

```python
import asyncio
import websockets
from japi import JapiProcessor

def handler(function_name, headers, input):
    if function_name == 'add':



japi_processor = JapiProcessor(handler)

async def setup(websocket, path):
    if path != '/api/v1':
        await websocket.send("invalid url")
        return

    async for input_json in websocket:

        output_json = japi_processor.process(input_json)

        await websocket.send(output_json)


async def main():
    async with websockets.serve(setup, "localhost", 8080):
        await asyncio.Future()

asyncio.run(main())
```
