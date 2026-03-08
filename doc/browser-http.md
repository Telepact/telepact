# Browser Client over HTTP

This guide shows the recommended shape for a browser client talking to a
Telepact server over ordinary HTTP.

## When to use this pattern

Use this pattern when:

- your client runs in a browser
- your server uses a Telepact library
- you want JSON on the wire for easy inspection and debugging

This is the common "web app" setup:

1. A Telepact schema defines the API.
2. A server library validates requests and responses.
3. An HTTP route accepts raw request bytes and returns raw response bytes.
4. A browser client uses `fetch` plus the Telepact `Client`.

## Server checklist

If your API does **not** define `struct.Auth_`, disable auth enforcement on the
server:

- TypeScript: `options.authRequired = false`
- Python: `options.auth_required = False`
- Java: `options.authRequired = false`
- Go: `options.AuthRequired = false`

If your browser client is served from a different origin, also enable the
appropriate CORS policy on your HTTP server.

## Python server example

```py
from telepact import Message, Server, TelepactSchema, TelepactSchemaFiles
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

files = TelepactSchemaFiles("./api")
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)

async def handler(request_message: Message) -> Message:
    function_name = next(iter(request_message.body.keys()))

    if function_name == "fn.greet":
        args = request_message.body[function_name]
        return Message({}, {"Ok_": {"message": f"Hello {args['subject']}!"}})

    raise RuntimeError(f"Unknown function: {function_name}")

options = Server.Options()
options.auth_required = False
server = Server(schema, handler, options)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api")
async def telepact_http(request: Request) -> Response:
    request_bytes = await request.body()
    response = await server.process(request_bytes)
    return Response(content=response.bytes, media_type="application/json")
```

## TypeScript browser client example

```ts
import { Client, ClientOptions, Message, Serializer } from 'telepact';

const adapter = async (message: Message, serializer: Serializer): Promise<Message> => {
    const requestBytes = serializer.serialize(message);

    const response = await fetch('http://127.0.0.1:8000/api', {
        method: 'POST',
        headers: {
            'content-type': 'application/json',
        },
        body: requestBytes,
    });

    if (!response.ok) {
        throw new Error(`Transport error: ${response.status}`);
    }

    const responseBytes = new Uint8Array(await response.arrayBuffer());
    return serializer.deserialize(responseBytes);
};

const options = new ClientOptions();
options.alwaysSendJson = true;
options.useBinary = false;

const client = new Client(adapter, options);

const response = await client.request(
    new Message({}, { 'fn.greet': { subject: 'Telepact' } }),
);
```

## Notes

- Telepact stays transport-agnostic; HTTP routing, CORS, and deployment remain
  your responsibility.
- `alwaysSendJson = true` is the easiest starting point for browser clients.
- If you only need a minimal integration and do not want the Telepact TS
  client, you can also send the raw two-element JSON envelope directly with
  `fetch`.
- To generate typed bindings for browser clients and servers, use
  `telepact codegen` from the
  [CLI](https://github.com/Telepact/telepact/blob/main/sdk/cli/README.md).
