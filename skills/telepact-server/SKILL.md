---
name: telepact-server
description: Implement a Telepact server for an already-drafted Telepact API schema using a Telepact server library in Go, Java, Python, or TypeScript. Use when agent needs to load an existing `.telepact.yaml` or `.telepact.json` schema, construct a `Server`, write handler dispatch code, and wire raw request/response bytes into a transport such as HTTP, WebSockets, NATS, or another request/reply channel.
---

# Telepact Server

Use this skill after the Telepact API schema already exists and is ready to serve.

Do not use this skill to design the schema itself. If the API contract is missing or unclear, draft the schema first, then come back and implement the server.

## Scope

This skill is for building the server side of a Telepact API with one of the Telepact libraries.

The server must use a Telepact library. Clients may use as much or as little Telepact tooling as they want, but a Telepact server is expected to run through the library so the ecosystem stays interoperable.

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
For Telepact design decisions around auth, optional headers, and transport
ownership, see the [FAQ](https://github.com/Telepact/telepact/blob/main/doc/05-background-and-reference/01-faq.md).

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

## Auth

If the API uses credentials, always model them as `union.Auth_` and flow them through the `@auth_` header.

Do not invent alternate credential channels such as:

- custom headers like `@token`, `@session`, or `Authorization`
- request body fields on ordinary functions
- transport-specific side channels that bypass the Telepact message

The Telepact ecosystem expects credentials to move through `union.Auth_` and `@auth_`. That path is treated with greater sensitivity. Outside it, Telepact has no equivalent guardrails, and credentials are easier to leak accidentally through logs, copied payloads, examples, or tooling.

Server rule:

- define `union.Auth_` in the schema when the API is authenticated
- declare `@auth_` as `union.Auth_` in the schema's headers definition
- read credentials from the request headers, not from ordinary function arguments
- keep auth handling inside the Telepact message flow rather than transport-specific side channels

If the API does not need authentication, omit `union.Auth_` and `@auth_` entirely. Do not create custom credential placeholders.

## Language Quick Reference

Use these library patterns directly for schema loading, handler definition, server construction, and a minimal request/reply transport hookup.

These are intentionally small end-to-end examples. In a real application, the transport wrapper is usually defined elsewhere and can be more elaborate, but the core request-bytes to response-bytes flow should stay the same.

### TypeScript

Schema loading and server setup:

```ts
import * as fs from 'fs';
import * as path from 'path';
import {
    FunctionRouter,
    Message,
    Server,
    ServerOptions,
    TelepactSchema,
    TelepactSchemaFiles,
} from 'telepact';

const files = new TelepactSchemaFiles('/path/to/schema/dir', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);

const functionRoutes = {
    'fn.example': async (functionName: string, requestMessage: Message): Promise<Message> => {
        const args = requestMessage.body[functionName];
        return new Message({}, { Ok_: {} });
    },
};

const options = new ServerOptions();
const functionRouter = new FunctionRouter();
functionRouter.registerUnauthenticatedRoutes(functionRoutes);
const telepactServer = new Server(schema, functionRouter, options);

// Assuming `transport` is defined elsewhere
transport.receive(async (requestBytes: Uint8Array): Promise<Uint8Array> => {
    const response = await telepactServer.process(requestBytes);
    return response.bytes;
});
```

### Python

Schema loading and server setup:

```py
from telepact import FunctionRouter, Message, Server, TelepactSchema, TelepactSchemaFiles

files = TelepactSchemaFiles('/path/to/schema/dir')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)

async def example(request_message: 'Message') -> 'Message':
    function_name = next(iter(request_message.body))
    args = request_message.body[function_name]
    return Message({}, {'Ok_': {}})

options = Server.Options()
function_routes = {'fn.example': lambda function_name, request_message: example(request_message)}
function_router = FunctionRouter()
function_router.register_unauthenticated_routes(function_routes)
telepactServer = Server(schema, function_router, options)

# Assuming `transport` is defined elsewhere
async def transport_handler(request_bytes: bytes) -> bytes:
    response = await telepactServer.process(request_bytes)
    return response.bytes

transport.receive(transport_handler)
```

### Java

Schema loading and server setup:

```java
var files = new TelepactSchemaFiles("/path/to/schema/dir");
var schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);

Map<String, FunctionRoute> functionRoutes = Map.of(
    "fn.example",
    (functionName, requestMessage) -> {
        var args = (Map<String, Object>) requestMessage.body.get(functionName);
        return new Message(Map.of(), Map.of("Ok_", Map.of()));
    }
);

var options = new Server.Options();
var functionRouter = new FunctionRouter();
functionRouter.registerUnauthenticatedRoutes(functionRoutes);
var telepactServer = new Server(schema, functionRouter, options);

// Assuming `transport` is defined elsewhere
transport.receive((requestBytes) -> {
    var response = telepactServer.process(requestBytes);
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

functionRoutes := map[string]telepact.FunctionRoute{
    "fn.example": func(functionName string, request telepact.Message) (telepact.Message, error) {
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
    },
}

telepactOptions := telepact.NewServerOptions()
functionRouter := telepact.NewFunctionRouter()
functionRouter.RegisterUnauthenticatedRoutes(functionRoutes)
telepactServer, err := telepact.NewServer(schema, functionRouter, telepactOptions)
if err != nil {
    return err
}

// Assuming `transport` is defined elsewhere
transport.Receive(func(requestBytes []byte) ([]byte, error) {
    response, _ := telepactServer.Process(requestBytes)
    return response.Bytes, nil
})
```

## Server Authoring Rules

- Assume the schema is the source of truth.
- Load the schema from `.telepact.yaml` or `.telepact.json` files before constructing the server. Prefer YAML for checked-in schema authoring.
- When loading a schema directory, treat it as the unordered union of the immediate `*.telepact.yaml` and `*.telepact.json` files in that directory. Do not rely on file order. Subdirectories are rejected.
- Keep transport code thin: receive bytes, call `server.process`, return bytes.
- Keep business logic in the handler, not in the transport.
- Return schema-valid `Message` objects from the handler.
- Let the Telepact library handle validation, built-in endpoints, binary negotiation, and response shaping.

## Standard Workflow

1. Locate the already-authored schema directory or schema file set.
2. Load those schema files into the language's `TelepactSchema`.
3. Write a handler that dispatches on the called function name.
4. Construct a `FunctionRouter` from your function routes, then pass it to `Server(schema, functionRouter, options)`.
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

If the input is a schema directory, the helper should read only the immediate
supported schema files in that directory. Mixed YAML and JSON is fine.
Collisions across files should be treated the same way they would be in a
single-file schema.

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

1. Read raw request body bytes from a POST request
2. Call `server.process(requestBytes)`
3. Write `response.bytes` to the HTTP response body
4. Set content type based on response headers only if your framework requires it

If your stack needs a media type, send JSON by default, and send octet-stream when the response indicates binary transport.

The following example is illustrative only. Express is just one common way to wire up an HTTP transport. Any framework is fine if it preserves the same raw-bytes request/reply boundary.

TypeScript with Express:

```ts
import express from 'express';

const app = express();

app.post('/api/telepact', express.raw({ type: '*/*' }), async (req, res) => {
    const requestBytes = new Uint8Array(req.body as Buffer);
    const response = await telepactServer.process(requestBytes);
    const mediaType = '@bin_' in response.headers
        ? 'application/octet-stream'
        : 'application/json';

    res.type(mediaType);
    res.send(Buffer.from(response.bytes));
});
```

### WebSockets

Typical WebSocket shape:

1. Receive one message frame as bytes
2. Call `server.process(frameBytes)`
3. Send the resulting `response.bytes` as the reply frame

Do not try to interpret the WebSocket payload as function-specific JSON outside the Telepact library.

Illustrative Python example with the `websockets` library:

```py
import asyncio
import websockets

async def telepact_websocket(websocket) -> None:
    async for request_bytes in websocket:
        if isinstance(request_bytes, str):
            request_bytes = request_bytes.encode('utf-8')

        telepact_response = await telepactServer.process(request_bytes)
        await websocket.send(telepact_response.bytes)

async def main() -> None:
    async with websockets.serve(telepact_websocket, '0.0.0.0', 8765):
        await asyncio.Future()
```

### Other Request/Reply Transports

For NATS, AMQP RPC, local IPC, or custom transports:

1. Receive raw bytes from the request channel
2. Pass them to `server.process`
3. Return the response bytes on the paired reply channel

If the transport is synchronous request/reply, the integration is usually a very thin wrapper.

Illustrative Go example with NATS request/reply:

```go
import "github.com/nats-io/nats.go"

_, err = nc.Subscribe("api.telepact", func(msg *nats.Msg) {
    response, _ := telepactServer.Process(msg.Data)

    if msg.Reply != "" {
        _ = nc.Publish(msg.Reply, response.Bytes)
    }
})
if err != nil {
    return err
}
```

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

For the full `_ext.Select_` shape and worked examples of how selection changes
response payloads, see:
https://raw.githubusercontent.com/Telepact/telepact/main/doc/02-design-apis/03-extensions.md

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

Check whether the schema defines `union.Auth_`.

- If the API is authenticated in the Telepact-standard way, keep `union.Auth_` in the schema and configure the server normally.
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

define functionRoutes mapping fn.* names to handlers:
    inspect called fn.*
    run business logic
    return Message(headers, resultUnion)

functionRouter = FunctionRouter()
functionRouter.register_unauthenticated_routes(functionRoutes)
telepactServer = Server(schema, functionRouter, options)

transport.on_request(requestBytes):
    response = telepactServer.process(requestBytes)
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
- any auth option changes match the presence or absence of `union.Auth_`

When the user asks for a Telepact server, assume they want working code, not just an explanation.
