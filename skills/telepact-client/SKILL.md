---
name: telepact-client
description: Implement a Telepact client for an already-drafted Telepact API schema in Go, Java, Python, TypeScript, or a raw transport stack. Use when agent needs to call `fn.*` endpoints by constructing Telepact request messages, handling `Ok_` or error result unions, wiring a transport adapter into a Telepact `Client`, or manually sending Telepact JSON over HTTP, WebSockets, NATS, or another request/reply channel.
---

# Telepact Client

Use this skill after the Telepact API schema already exists and the task is to call it from a client.

Do not use this skill to design the schema itself. If the API contract is missing or unclear, draft the schema first, then come back and implement the client.

## Scope

This skill is for building the client side of a Telepact API.

Unlike servers, clients may use as much or as little Telepact tooling as they want:

- a raw client that sends Telepact JSON over an existing transport
- a Telepact library `Client` in Go, Java, Python, or TypeScript

## First Step

Classify the job before writing code:

1. Decide whether this should be a raw client or a Telepact-library client.
2. Identify the stack: TypeScript, Python, Java, Go, or another environment.
3. Locate the target schema or at least the specific `fn.*` definitions being called.
4. Decide whether the client only needs JSON, or whether it also needs Telepact features such as response field selection or binary negotiation.

Default rule:

- If the client only needs a few straightforward calls and cannot take a dependency, use raw JSON.
- If the client needs binary, serializer support, transport reuse, or richer Telepact behavior, use the Telepact library.

## Core Mental Model

A Telepact client sends one Telepact message and receives one Telepact message back.

The envelope is always:

```json
[headers, body]
```

Where:

- `headers` is a JSON object for cross-cutting behavior such as `@id_`, `@time_`, `@select_`, or auth headers
- `body` is a JSON object with exactly one top-level tag

For requests, that tag is the called function:

```json
[{}, {"fn.add": {"x": 1, "y": 2}}]
```

For responses, that tag is the result union case:

```json
[{}, {"Ok_": {"result": 3}}]
```

or:

```json
[{}, {"ErrorCannotDivideByZero": {}}]
```

The schema defines:

- the argument object for each `fn.*`
- the result union for each `fn.*`
- any shared `errors.*`
- any request and response headers from `headers.*`

Important:

- The base Telepact `Client` library does not load the schema and does not become your type system.
- The schema is still the source of truth for argument shapes, result tags, and header names.
- A raw client and a Telepact-library client must both obey the same on-the-wire message format.

## Built-In Functions And Common Headers

Every Telepact API includes standard built-ins such as:

- `fn.ping_` for connectivity checks
- `fn.api_` for fetching the served schema

Recommended discovery flow before integrating:

1. call `fn.ping_` to confirm the server is reachable
2. call `fn.api_` with `{}` to inspect the user-facing API surface
3. call `fn.api_` with `{"includeInternal!": true}` when you need the full schema including Telepact internal definitions

Examples:

```json
[{}, {"fn.ping_": {}}]
```

```json
[{}, {"fn.api_": {}}]
```

```json
[{}, {"fn.api_": {"includeInternal!": true}}]
```

Use the default `fn.api_` call for normal integration work. Use `includeInternal!` when you need to see the complete set of functions and built-in definitions available on that Telepact server.

Common client-facing headers include:

- `@time_`: request timeout in milliseconds
- `@id_`: correlation ID reflected by the server
- `@select_`: response field selection
- `@auth_`: auth data when the schema defines `union.Auth_`
- `@warn_`: warnings returned by the server
- `@bin_`, `@enc_`, `@pac_`: binary negotiation headers (though should not use directly)

For JSON mode, API schema fields that have the `bytes` type travel as base64 strings.

## Auth

If the server schema defines `union.Auth_`, send credentials in the `@auth_` header. The value inside `@auth_` must match one variant of `union.Auth_` exactly.

For example, if the schema includes:

```yaml
union.Auth_:
  - Token:
      token: string
```

then a client request should look like:

```json
[
    {
        "@auth_": {
            "Token": {
                "token": "***"
            }
        }
    },
    {
        "fn.getProfile": {}
    }
]
```

Using the Telepact library, that becomes:

```ts
const request = new Message(
    {
        '@auth_': {
            token: 'secret-token',
        },
    },
    {
        'fn.getProfile': {},
    },
);
```

If the API does not use auth, omit `@auth_`.

## Path A: Raw Client

Use this path when you do not want a Telepact dependency.

### Raw Client Workflow

1. Read the target `fn.*` argument and result definitions from the schema.
2. Build a Telepact message as `[headers, {"fn.name": args}]`.
3. JSON-encode it as UTF-8 bytes.
4. Send those bytes over the transport.
5. Parse the response as `[responseHeaders, {"Ok_"|errorTag: payload}]`.
6. Branch on the response tag, not on transport status codes alone.

Example request:

```json
[{"@id_": "call-123"}, {"fn.exportVariables": {"limit!": 1}}]
```

Example response:

```json
[{"@id_": "call-123"}, {"Ok_": {"variables": [{"name": "a", "value": 1}]}}]
```

### Raw Client Rules

- Never send only the function arguments by themselves. Always send the two-element Telepact envelope.
- Preserve exact schema field names, including optional names like `limit!`.
- Treat non-`Ok_` tags as schema-level outcomes, not necessarily transport failures.
- Base64-encode `bytes` fields when you are using JSON.
- Prefer JSON-only raw clients unless binary is a hard requirement.

### Raw Response Selection

`@select_` lets the client ask the server to trim response payloads.

For the full `_ext.Select_` shape and more end-to-end examples, see:
https://raw.githubusercontent.com/Telepact/telepact/main/doc/02-design-apis/03-extensions.md

Common patterns:

```json
[
    {
        "@select_": {
            "struct.User": ["id", "displayName!"],
            "->": {
                "Ok_": ["users"]
            }
        }
    },
    {
        "fn.listUsers": {}
    }
]
```

For unions, select by tag:

```json
{
    "@select_": {
        "union.SearchResult": {
            "User": ["id", "displayName!"]
        }
    }
}
```

If the header shape does not match the schema, the server will return `ErrorInvalidRequestHeaders_`.

### Raw Binary Guidance

Manual binary support is possible, but it is not the default recommendation.

Use manual binary only if you fully control both ends and have a concrete reason to avoid JSON. Otherwise, use the Telepact library client instead.

If you must implement it manually:

- the client advertises known encodings with `@bin_`
- the server responds with `@bin_`
- when the checksum is unknown to the client, the server also returns `@enc_`
- `@pac_` opts into packed binary form
- on `ErrorParseFailure_` with `IncompatibleBinaryEncoding`, retry after updating the encoding map or fall back to JSON

## Path B: Telepact Library Client

Use this path when you want Telepact-aware serialization and request handling.

Install the matching library first:

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

Then implement the same three-part pattern in that language:

1. Build a transport adapter over request and response bytes
2. Construct a Telepact `Client`
3. Send `Message(headers, {"fn.name": args})` through `client.request(...)`

## What The Library Is Doing

The Telepact `Client` library is protocol-aware, but schema-agnostic.

It handles:

- serializing a `Message` to wire bytes
- deserializing response bytes back into a `Message`
- JSON/base64 conversion for `bytes` fields
- defaulting `@time_` when the request does not provide one
- binary negotiation bookkeeping when `useBinary` is enabled
- retrying once when the server reports `IncompatibleBinaryEncoding`

It does not:

- validate your request body against the schema
- validate the server's `Ok_` payload against the schema
- replace generated types or schema reading

So the correct layering is:

- application code decides which `fn.*` to call and what message to build
- the Telepact client library handles serialization details and protocol mechanics
- the transport adapter only moves bytes

## Language Quick Reference

### TypeScript

```ts
import { Client, ClientOptions, Message, Serializer } from 'telepact';

const adapter = async (requestMessage: Message, serializer: Serializer): Promise<Message> => {
    const requestBytes = serializer.serialize(requestMessage);

    // Assuming `transport` is defined elsewhere
    const responseBytes = await transport.send(requestBytes);

    return serializer.deserialize(responseBytes);
};

const options = new ClientOptions();
options.useBinary = true;
options.alwaysSendJson = false;

const client = new Client(adapter, options);

const response = await client.request(
    new Message(
        { '@select_': { '->': { Ok_: ['summary'] } } },
        { 'fn.getDashboard': {} },
    ),
);
```

Notes:

- `localStorageCacheNamespace` can be set when you want browser-backed binary encoding cache reuse.

### Python

```py
from telepact import Client, Message, Serializer

async def adapter(request_message: Message, serializer: Serializer) -> Message:
    request_bytes = serializer.serialize(request_message)

    # Assuming `transport` is defined elsewhere
    response_bytes = await transport.send(request_bytes)

    return serializer.deserialize(response_bytes)

options = Client.Options()
options.use_binary = True
options.always_send_json = False

client = Client(adapter, options)

response = await client.request(
    Message(
        {'@select_': {'->': {'Ok_': ['summary']}}},
        {'fn.getDashboard': {}},
    )
)
```

### Java

```java
BiFunction<Message, Serializer, Future<Message>> adapter = (requestMessage, serializer) -> {
    return CompletableFuture.supplyAsync(() -> {
        var requestBytes = serializer.serialize(requestMessage);

        // Assuming `transport` is defined elsewhere
        var responseBytes = transport.send(requestBytes);

        return serializer.deserialize(responseBytes);
    });
};

var options = new Client.Options();
options.useBinary = true;
options.alwaysSendJson = false;

var client = new Client(adapter, options);
var response = client.request(
    new Message(
        Map.of("@select_", Map.of("->", Map.of("Ok_", List.of("summary")))),
        Map.of("fn.getDashboard", Map.of())
    )
);
```

### Go

```go
adapter := func(ctx context.Context, request telepact.Message, serializer *telepact.Serializer) (telepact.Message, error) {
    requestBytes, err := serializer.Serialize(request)
    if err != nil {
        return telepact.Message{}, err
    }

    // Assuming `transport` is defined elsewhere
    responseBytes, err := transport.Send(ctx, requestBytes)
    if err != nil {
        return telepact.Message{}, err
    }

    return serializer.Deserialize(responseBytes)
}

options := telepact.NewClientOptions()
options.UseBinary = true
options.AlwaysSendJSON = false

client, err := telepact.NewClient(adapter, options)
if err != nil {
    return err
}

response, err := client.Request(
    telepact.NewMessage(
        map[string]any{
            "@select_": map[string]any{
                "->": map[string]any{
                    "Ok_": []any{"summary"},
                },
            },
        },
        map[string]any{
            "fn.getDashboard": map[string]any{},
        },
    ),
)
```

## Standard Workflow

1. Inspect the schema for the target `fn.*`, result union, and any relevant headers.
2. Use `fn.ping_` and then `fn.api_` to confirm connectivity and inspect the server before wiring real calls.
3. Use `{"includeInternal!": true}` with `fn.api_` when you need the full available function surface, including Telepact internal definitions.
4. Decide whether the client should be raw JSON or Telepact-library based.
5. Implement the real function calls with exact Telepact message envelopes.
6. Add optional headers such as `@id_`, `@auth_`, or `@select_` only when they are actually needed.
7. Reach for binary only after the JSON path is already working.

## Client Authoring Rules

- Assume the schema is the source of truth.
- Build messages with one request target and one response result tag.
- Keep transport code thin: send bytes, receive bytes, deserialize if needed.
- Inspect response tags like `Ok_` or `ErrorSomething`, not only transport status.
- Use `fn.ping_` for connectivity checks and `fn.api_` for schema discovery.
- Use `fn.api_` with `includeInternal!` when you need to inspect the complete server surface before or during integration.
- For raw clients, prefer JSON first and add manual binary only with a clear need.
- For library clients, let the serializer and client handle bytes/base64 and binary negotiation rather than duplicating that logic in application code.

## Debugging Checklist

- If the server says `ErrorInvalidRequestBody_`, compare your function name and argument object directly to the schema.
- If the server says `ErrorInvalidRequestHeaders_`, check `@select_`, auth headers, and header value types.
- If a `bytes` field looks wrong in JSON mode, check whether you forgot base64 encoding or decoding.
- If binary mode fails with `IncompatibleBinaryEncoding`, retry through the library client or refresh your encoding map before sending another binary request.
- If the server keeps returning `ErrorUnknown_`, validate the transport first with `fn.ping_` and then inspect the actual response headers and body rather than assuming an HTTP-layer problem.
