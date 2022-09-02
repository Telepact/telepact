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
    "cases": {
      "{case-name}": "{type}",
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
style and `{function-name}`/`{field-name}`/`{case-name}` follow `lowerCamelCase`
style.

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

  "error.VariableNotFound": {
    "doc": "Indicates a computation used a variable that has not been stored.",
    "fields": {
      "message": "string",
      "var": "string"
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

## 3.2 JAPI Payloads

JAPI payloads are pure JSON payloads that indicate interactions with the API,
such as function calls, function returns, or emitted events.

### 3.2.0 Format

All JAPI payloads follow the same general format, a JSON array with 3 elements,
a string indicating the payload type, an object containing headers, and an
object containing the primary body of data.

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

### 3.2.1 Function Input JAPI Payload

A Function Input JAPI payload has has `{payload-type}` of
`function.{function-name}`, where `{function-name}` is defined in the JAPI
Description.

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

### 3.2.2 Function Output JAPI Payload

A Function Output JAPI Payload has the `{payload-type}` of
`function.{function-name}.result`, where `{function-name}` is defined in the
JAPI Description.

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

### 3.2.3 Error JAPI Payload

An Error JAPI Payload has the `{payload-type}` of `error.{error-name}`, where
`{error-name}` is defined in the JAPI Description.

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

### 3.2.4 Event JAPI Payload

An Event JAPI Payload has the `{payload-type}` of `event.{type-name}` where
`{type-name}` is defined by the JAPI Description.

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

For JAPI providers offering functions for consumers to invoke, the JAPI provider
implementation MUST set up a transport that allows for both receiving and
sending JSON payloads to and from an API consumer. The full interaction will
consist of the following:

1. the sending of a Function Input JAPI Payload from a consumer that is received
   by the provider implementation through it's chosen IPC boundary,
2. the passing of that JSON payload to a JAPI processor for deserialization and
   validation
3. the passing of the deserialized data from the function input payload to
   handlers implemented by the API provider to perform a function call,
4. the returning of the result of that function call back to the JAPI processor
   for validation and serialization into a Function Output JAPI payload
5. the sending of that JSON payload from the provider to the consumer through
   the IPC boundary

HTTP Example:

```java
import io.javalin.Javalin;
import io.github.brenbar.japi.JapiProcessor;

public class Main {

    public static void main(String[] args) {
        var japiProcessor = new JapiProcessor(Main::handle);
        var app = Javalin.create().start(8080);
        app.get("/api/v1", ctx -> {
            // 1. Receive Function Input JAPI Payload from the consumer.
            String inputJson = ctx.body();

            // 2. Pass the JAPI payload to a JAPI processor, which will parse
            //    the JSON payload, validate the data against the JAPI
            //    Description, and pass validated data provider defined handler.
            String outputJson = japiProcessor.process(inputJson);

            // 5. Send Function Return JAPI payload to consumer.
            ctx.result(outputJson);
        });
    }

    private static Map<String, Object> handle(String functionName, Map<String, Object> headers, Map<String, Object> input) {
        // 3. Use deserialized and validated JAPI Function Input to perform
        //    function call
        Map<String, Object> result = switch (functionName) {
            case "compute" -> {
                // TODO
                yield Map.of("result", 0)
            }
            case "store" -> {
                // TODO
                yield Map.of();
            }
            default -> throw new RuntimeException();
        };

        // 4. Return function result back the JapiProcessor for validation
        //    against the JAPI description, and then serialization into a
        //    JAPI Function Output Payload.
        return result;
    }
}
```

Websocket Example

```python
import asyncio
import websockets
from japi import JapiProcessor

def handler(function_name, headers, input):
    # 3. Use deserialized and validated JAPI Function Input to perform
    #    function call
    result = {}
    if function_name == 'compute':
        # TODO
        result = {
            "result": 0
        }
    elif function_name == 'store':
        # TODO
        result = {}

    # 4. Return function result back the JapiProcessor for validation
    #    against the JAPI description, and then serialization into a
    #    JAPI Function Output Payload.
    return result


japi_processor = JapiProcessor(handler)

async def setup(websocket, path):
    if path != '/api/v1':
        await websocket.send("invalid url")
        return

    # 1. Receive Function Input JAPI Payload from the consumer.
    async for input_json in websocket:

        # 2. Pass the JAPI payload to a JAPI processor, which will parse
        #    the JSON payload, validate the data against the JAPI
        #    Description, and pass validated data provider defined handler.
        output_json = japi_processor.process(input_json)

        # 5. Send Function Return JAPI payload to consumer.
        await websocket.send(output_json)


async def main():
    async with websockets.serve(setup, "localhost", 8080):
        await asyncio.Future()

asyncio.run(main())
```
