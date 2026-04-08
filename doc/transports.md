# Transport Guide

Telepact is transport-agnostic by design.

That means the Telepact libraries own message validation, schema semantics,
request and response serialization, binary negotiation, and related ecosystem
features, while your application owns the transport boundary that moves bytes in
and out.

In practice, the transport boundary is usually quite small:

- server code receives request bytes from a transport
- the Telepact server turns those bytes into a validated response message
- server code sends the response bytes back over the transport
- client code serializes a Telepact message into request bytes
- the transport sends those bytes to the remote service
- client code deserializes the response bytes back into a Telepact message

This guide shows concrete examples for two common transports:

- HTTP
- WebSockets

Runnable counterparts live under [`example/`](../example/), including
[`example/py-links`](../example/py-links/README.md),
[`example/py-http-cookie-auth`](../example/py-http-cookie-auth/README.md), and
[`example/py-websocket`](../example/py-websocket/README.md).

The same pattern applies to NATS, stdio, queues, custom RPC layers, and other
IPC boundaries.

## The Core Cutpoint

The most important integration point is the raw byte boundary.

On the server side, the transport usually ends up calling:

```py
response = await server.process(request_bytes)
response_bytes = response.bytes
```

On the client side, the transport usually sits inside a Telepact adapter:

```py
async def adapter(message: Message, serializer: Serializer) -> Message:
    request_bytes = serializer.serialize(message)
    response_bytes = await transport.send(request_bytes)
    return serializer.deserialize(response_bytes)
```


## Example API

The examples below use this schema:

```yaml
- fn.greet:
    subject: string
  ->:
    Ok_:
      message: string
```

## HTTP

HTTP is the most common Telepact deployment shape. A typical setup is:

- one POST endpoint for Telepact requests
- request body contains Telepact request bytes
- response body contains Telepact response bytes
- `Content-Type` reflects whether the response is JSON or binary
- ordinary HTTP middleware can still sit around the Telepact core when needed

### HTTP server example (Python + Starlette)

```py
from telepact import Message, Server, TelepactSchema, TelepactSchemaFiles
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
import uvicorn

files = TelepactSchemaFiles('./api')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)

async def greet(function_name: str, request_message: Message) -> Message:
    arguments = request_message.body[function_name]
    subject = arguments['subject']
    return Message({}, {'Ok_': {'message': f'Hello {subject}!'}})

options = Server.Options()
options.auth_required = False
server = Server(schema, {'fn.greet': greet}, options)

async def http_handler(request):
    request_bytes = await request.body()

    # The transport cutpoint is tiny and explicit.
    response = await server.process(request_bytes)
    response_bytes = response.bytes

    media_type = (
        'application/octet-stream'
        if '@bin_' in response.headers
        else 'application/json'
    )
    return Response(content=response_bytes, media_type=media_type)

app = Starlette(routes=[
    Route('/api/telepact', endpoint=http_handler, methods=['POST']),
])

uvicorn.run(app, host='0.0.0.0', port=8000)
```

### HTTP client example (browser TypeScript + fetch)

```ts
import { Client, ClientOptions, Message, Serializer } from 'telepact';

const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
  const requestBytes = serializer.serialize(message);

  const response = await fetch('http://localhost:8000/api/telepact', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: requestBytes,
  });

  const responseBytes = new Uint8Array(await response.arrayBuffer());
  return serializer.deserialize(responseBytes);
};

const client = new Client(adapter, new ClientOptions());

const response = await client.request(
  new Message({}, { 'fn.greet': { subject: 'World' } }),
);

if (response.getBodyTarget() === 'Ok_') {
  console.log(response.getBodyPayload().message);
}
```

### HTTP notes

- `fetch` accepts binary request bodies, so the same client can work with JSON
  or binary Telepact payloads.
- Reverse proxies, CORS configuration, and other HTTP concerns still remain
  possible around a Telepact endpoint when your application needs them.

## WebSockets

WebSockets work well when you want a long-lived connection but still want your
application to exchange discrete Telepact request and response messages.

A common pattern is one Telepact request per WebSocket message and one Telepact
response per WebSocket message.

### WebSocket server example (Python + Starlette)

```py
from telepact import Message, Server, TelepactSchema, TelepactSchemaFiles
from starlette.applications import Starlette
from starlette.routing import WebSocketRoute
import uvicorn

files = TelepactSchemaFiles('./api')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)

async def greet(function_name: str, request_message: Message) -> Message:
    arguments = request_message.body[function_name]
    subject = arguments['subject']
    return Message({}, {'Ok_': {'message': f'Hello {subject}!'}})

options = Server.Options()
options.auth_required = False
server = Server(schema, {'fn.greet': greet}, options)

async def websocket_handler(websocket):
    await websocket.accept()
    try:
        while True:
            request_bytes = await websocket.receive_bytes()
            response = await server.process(request_bytes)
            await websocket.send_bytes(response.bytes)
    except Exception:
        await websocket.close()

app = Starlette(routes=[
    WebSocketRoute('/ws/telepact', endpoint=websocket_handler),
])

uvicorn.run(app, host='0.0.0.0', port=8000)
```

### WebSocket client example (browser TypeScript)

This example opens a new WebSocket per request to keep the example small.
Production clients will often reuse one socket and correlate in-flight requests
with an application-level request id in headers or payloads.

```ts
import { Client, ClientOptions, Message, Serializer } from 'telepact';

const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
  const requestBytes = serializer.serialize(message);

  const responseBytes = await new Promise<Uint8Array>((resolve, reject) => {
    const ws = new WebSocket('ws://localhost:8000/ws/telepact');
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => {
      ws.send(requestBytes);
    };

    ws.onmessage = (event) => {
      resolve(new Uint8Array(event.data as ArrayBuffer));
      ws.close();
    };

    ws.onerror = () => {
      reject(new Error('WebSocket transport failed'));
      ws.close();
    };
  });

  return serializer.deserialize(responseBytes);
};

const client = new Client(adapter, new ClientOptions());

const response = await client.request(
  new Message({}, { 'fn.greet': { subject: 'World' } }),
);

if (response.getBodyTarget() === 'Ok_') {
  console.log(response.getBodyPayload().message);
}
```

### WebSocket notes

- Reusing a single socket is usually better than reconnecting per request.
- If you multiplex requests over one socket, add an explicit correlation id so
  responses can be matched to callers.
- The transport cutpoint is also a natural place for heartbeat handling,
  connection lifecycle metrics, auth refresh, and backpressure policy.

## See also

- [Example](./example.md)
- [FAQ](./faq.md)
- [Runtime Error Guide](./runtime-errors.md)
