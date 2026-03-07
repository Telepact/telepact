---
name: telepact-server
description: Implement a Telepact server for an already-drafted Telepact API schema using a Telepact server library in Go, Java, Python, or TypeScript. Use when Codex needs to load an existing `.telepact.json` schema, construct a `Server`, write handler dispatch code, and wire raw request/response bytes into a transport such as HTTP, WebSockets, NATS, or another request/reply channel.
---

# Telepact Server

Use this skill after the Telepact API schema already exists and is ready to serve.

Do not use this skill to design the schema itself. If the API contract is missing or unclear, draft the schema first, then come back and implement the server.

## Scope

This skill is for building the server side of a Telepact API with one of the Telepact libraries.

The server must use a Telepact library. Clients may use as much or as little Telepact tooling as they want, but a Telepact server is expected to run through the library so the ecosystem stays interoperable.

This skill is intentionally self-contained. Do not assume you can open this repo's README files or internal schema files while using it.

## First Step

Classify the target stack first:

- TypeScript
- Python
- Java
- Go

Install the matching Telepact library first:

- TypeScript: `npm install telepact`
- Python: `pip install telepact`
- Java (Maven):

```xml
<dependency>
    <groupId>io.github.telepact</groupId>
    <artifactId>telepact</artifactId>
</dependency>
```

- Go: `go get github.com/telepact/telepact/lib/go`

Then implement the same four-part pattern in that language:

1. Load the existing Telepact schema
2. Define a handler over Telepact `Message` values
3. Construct a Telepact `Server`
4. Wire raw transport bytes into `server.process(...)`

## Core Mental Model

A Telepact server has four layers:

1. A drafted Telepact schema loaded into a `TelepactSchema`
2. A business-logic handler that accepts a parsed Telepact `Message` and returns a Telepact `Message`
3. A `Server` instance from the language library
4. A transport adapter that feeds raw `requestBytes` into `server.process(...)` and sends `response.bytes` back over HTTP, WebSocket, NATS, or similar

The important boundary is this:

- Your transport deals in bytes.
- Your handler deals in parsed Telepact messages.
- The Telepact library sits between them.

If the transport code starts switching on `fn.*` names or manually inspecting Telepact headers, the layering is wrong. Move that logic either into the handler or remove it and let the library do it.

## What The Library Is Doing

When you construct a Telepact `Server` with a loaded schema, the library is not just storing documentation. It uses the schema to enforce runtime interoperability.

The library handles:

- deserializing request bytes into the Telepact message envelope
- validating request headers against the schema and Telepact built-ins
- validating the request body against the called `fn.*` argument type
- decoding/coercing binary and `bytes`-related payload details when needed
- automatically serving built-in functions such as `fn.ping_` and `fn.api_`
- validating your handler's response body against the function result union
- validating response headers
- applying client-driven response field selection via `@select_`
- negotiating opt-in binary response behavior via Telepact headers
- distributing the loaded API schema through the always-on `fn.api_` endpoint

Do not manually re-implement those behaviors in your transport or business logic.

## Language Quick Reference

Use these library patterns directly for schema loading, handler definition, and server construction.

Do not treat the following snippets as the transport layer. The actual call to `server.process(...)` belongs in your HTTP, WebSocket, NATS, or other request/reply transport wrapper.

### TypeScript

Schema loading and server setup:

```ts
import * as fs from 'fs';
import * as path from 'path';
import {
    Message,
    Server,
    ServerOptions,
    TelepactSchema,
    TelepactSchemaFiles,
} from 'telepact';

const files = new TelepactSchemaFiles('/path/to/schema/dir', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);

const handler = async (requestMessage: Message): Promise<Message> => {
    const functionName = Object.keys(requestMessage.body)[0];
    const args = requestMessage.body[functionName];
    return new Message({}, { Ok_: {} });
};

const server = new Server(schema, handler, new ServerOptions());

// Assuming `transport` is defined elsewhere
transport.receive(async (requestBytes: Uint8Array): Promise<Uint8Array> => {
    const response = await server.process(requestBytes);
    return response.bytes;
});
```

### Python

Schema loading and server setup:

```py
from telepact import Message, Server, TelepactSchema, TelepactSchemaFiles

files = TelepactSchemaFiles('/path/to/schema/dir')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)

async def handler(request_message: 'Message') -> 'Message':
    function_name = next(iter(request_message.body))
    args = request_message.body[function_name]
    return Message({}, {'Ok_': {}})

options = Server.Options()
server = Server(schema, handler, options)

# Assuming `transport` is defined elsewhere
async def transport_handler(request_bytes: bytes) -> bytes:
    response = await server.process(request_bytes)
    return response.bytes

transport.receive(transport_handler)
```

### Java

Schema loading and server setup:

```java
var files = new TelepactSchemaFiles("/path/to/schema/dir");
var schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);

Function<Message, Message> handler = (requestMessage) -> {
    var functionName = requestMessage.body.keySet().stream().findAny().orElseThrow();
    var args = (Map<String, Object>) requestMessage.body.get(functionName);
    return new Message(Map.of(), Map.of("Ok_", Map.of()));
};

var options = new Server.Options();
var server = new Server(schema, handler, options);

// Assuming `transport` is defined elsewhere
transport.receive((requestBytes) -> {
    var response = server.process(requestBytes);
    return response.bytes;
});
```

### Go

Schema loading and server setup:

```go
files, err := telepact.NewTelepactSchemaFiles("/path/to/schema/dir")
if err != nil {
    return err
}

schema, err := telepact.TelepactSchemaFromFileJSONMap(files.FilenamesToJSON)
if err != nil {
    return err
}

handler := func(request telepact.Message) (telepact.Message, error) {
    functionName, err := request.BodyTarget()
    if err != nil {
        return telepact.Message{}, err
    }

    args, err := request.BodyPayload()
    if err != nil {
        return telepact.Message{}, err
    }

    _ = functionName
    _ = args

    return telepact.NewMessage(
        map[string]any{},
        map[string]any{"Ok_": map[string]any{}},
    ), nil
}

server, err := telepact.NewServer(schema, handler, telepact.NewServerOptions())
if err != nil {
    return err
}

// Assuming `transport` is defined elsewhere
transport.Receive(func(requestBytes []byte) ([]byte, error) {
    response, err := server.Process(requestBytes)
    if err != nil {
        return nil, err
    }
    return response.Bytes, nil
})
```

## Server Authoring Rules

- Assume the schema is the source of truth.
- Load the schema from `.telepact.json` files before constructing the server.
- Keep transport code thin: receive bytes, call `server.process`, return bytes.
- Keep business logic in the handler, not in the transport.
- Return schema-valid `Message` objects from the handler.
- Let the Telepact library handle validation, built-in endpoints, binary negotiation, and response shaping.

## Standard Workflow

1. Locate the already-authored schema directory or schema file set.
2. Load those schema files into the language's `TelepactSchema`.
3. Write a handler that dispatches on the called function name.
4. Construct `Server(schema, handler, options)`.
5. Connect your transport's incoming raw bytes to `server.process(...)`.
6. Return `response.bytes` directly to the caller.
7. Only add transport-level details outside the server, such as route registration, connection setup, or content-type mapping.

## Loading The Schema

Follow the library's normal schema-loading path rather than rolling your own parser.

The common pattern is:

1. Read one schema file or a schema directory
2. Build a `TelepactSchemaFiles` or equivalent helper
3. Build `TelepactSchema` from the discovered file JSON map
4. Pass that schema into the `Server`

Use the constructor names shown in this skill. Do not invent alternate schema loaders if the library already provides one.

## Handler Shape

Your handler should operate on parsed Telepact messages, not on raw sockets or HTTP objects.

Typical flow:

1. Inspect the body target to find the requested function, such as `fn.createUser`
2. Read the function argument payload
3. Run business logic
4. Return a Telepact `Message` whose body is one result tag such as `Ok_` or a declared error tag

Keep the handler focused on domain behavior:

- authentication decisions
- database reads and writes
- authorization checks
- application-specific validation beyond schema shape
- constructing schema-valid result payloads

Do not manually:

- parse the request envelope
- validate request payload shapes
- perform `fn.api_` dispatch
- implement `@select_`
- negotiate binary encoding

Those are library responsibilities.

## Transport Pattern

The transport adapter should be almost trivial.

Generic shape:

```text
receive request bytes
-> call server.process(requestBytes)
-> get response.bytes
-> send those bytes back unchanged
```

This pattern works for:

- HTTP POST
- WebSocket request/reply messages
- NATS request/reply
- TCP framed messages
- worker queues where a request expects a direct response

### HTTP

Typical HTTP shape:

1. Read raw request body bytes
2. Call `server.process(requestBytes)`
3. Write `response.bytes` to the HTTP response body
4. Set content type based on response headers only if your framework requires it

If your stack needs a media type, send JSON by default, and send octet-stream when the response indicates binary transport.

### WebSockets

Typical WebSocket shape:

1. Receive one message frame as bytes
2. Call `server.process(frameBytes)`
3. Send the resulting `response.bytes` as the reply frame

Do not try to interpret the WebSocket payload as function-specific JSON outside the Telepact library.

### Other Request/Reply Transports

For NATS, AMQP RPC, local IPC, or custom transports:

1. Receive raw bytes from the request channel
2. Pass them to `server.process`
3. Return the response bytes on the paired reply channel

If the transport is synchronous request/reply, the integration is usually a very thin wrapper.

## Built-In Telepact Server Behavior

Telepact servers automatically expose some server behavior based on the loaded schema and Telepact internals.

### `fn.api_`

`fn.api_` is automatically available and returns the loaded API schema.

This matters because it enables:

- console browsing
- mocking workflows
- schema retrieval by tools
- introspection without adding custom metadata routes

Do not hand-write a duplicate "get schema" function unless the user explicitly wants a separate domain-level endpoint.

### `fn.ping_`

`fn.ping_` is automatically available as a basic connectivity check.

### Validation Errors

The runtime also provides standard invalid-request and invalid-response errors for compatibility enforcement. This is part of why the server library is mandatory for Telepact servers.

Common automatically available behavior includes:

- `fn.ping_` for a minimal liveness check
- `fn.api_` for returning the loaded schema
- standard invalid-request and invalid-response error handling
- built-in headers for selection, binary negotiation, warnings, IDs, and related protocol features

## Client-Driven Features The Server Handles Opaquely

A Telepact client can opt into ecosystem features using headers. The server library handles these features based on the loaded schema.

### Response Field Selection

Clients may request struct field selection using `@select_`.

Your server code should not implement custom pruning logic. Return the full schema-valid response and let the Telepact runtime shape the response according to the selection header.

Important:

- field selection applies to struct-shaped response data
- it does not exist so application code can invent ad hoc sparse payload rules
- function argument links are intentionally preserved as Telepact defines them

### Binary Negotiation

Clients may opt into binary encoding behavior with Telepact binary headers.

Your transport should still follow the same byte pipeline:

`request bytes -> server.process -> response bytes`

Do not add custom binary serializers around Telepact messages. The library already negotiates supported encodings, emits binary-related headers, and performs the necessary encoding/decoding work.

### `bytes` Values

If the schema contains `bytes` fields, the Telepact runtime handles the schema-aware coercion and response metadata needed for those payloads. Do not hand-roll per-function `bytes` conversions.

## Error Handling Guidance

If the handler raises or returns an invalid response, the Telepact runtime will convert that into Telepact-compatible error behavior.

Good practice:

- use the library's error hooks or callbacks if available
- log request start/end and failures near the handler boundary
- keep transport exceptions separate from domain exceptions

If you need middleware-like behavior, place it near the start and end of the handler or use the library's request/response hooks where available.

## Auth Guidance

Check whether the schema defines `struct.Auth_`.

- If the API is authenticated in the Telepact-standard way, keep `struct.Auth_` in the schema and configure the server normally.
- If the server is intentionally unauthenticated, disable the library option that otherwise requires auth.

Do not invent parallel auth envelope formats when the Telepact auth pattern already fits the task.

In some libraries, auth is required by default unless disabled in server options. If the API is intentionally unauthenticated, set the option accordingly instead of fighting the runtime.

## Delivery Expectations

When implementing a Telepact server, produce:

- schema loading code
- a handler with clear function dispatch
- server construction
- transport wiring that passes raw bytes through `server.process`

Prefer complete runnable server code over abstract guidance when the user asks to implement something in the repo.

## Minimal Pseudocode

```text
load schema files
build TelepactSchema

define handler(message):
    inspect called fn.*
    run business logic
    return Message(headers, resultUnion)

server = Server(schema, handler, options)

transport.on_request(requestBytes):
    response = server.process(requestBytes)
    return response.bytes
```

## Final Checklist

Before finishing, verify:

- a Telepact schema already exists and is being loaded, not re-invented
- the code uses a Telepact `Server` from the correct language library
- the transport passes raw bytes into `server.process(...)`
- the transport returns `response.bytes` directly
- the handler returns Telepact `Message` values, not framework-native payload objects
- the handler only implements domain logic
- `fn.api_` is not redundantly re-implemented
- binary negotiation and field selection are left to the runtime
- any auth option changes match the presence or absence of `struct.Auth_`

When the user asks for a Telepact server, assume they want working code, not just an explanation.
