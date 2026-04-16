# Telepact Library for TypeScript

## Installation

```sh
npm install telepact
```

## Recommended TypeScript/browser path

For browser clients, the recommended workflow is:

1. use plain JSON plus `fetch` for a first smoke test or browser-console call
2. move to the Telepact TypeScript library for the real application client
3. add generated bindings later if the app wants typed function wrappers

In practice, most browser apps should use:

- one `Client` per Telepact endpoint
- one small transport adapter per transport (`fetch` first, WebSocket only when needed)
- ordinary app code that builds `Message` requests and switches on response unions

Keep the adapter thin: serialize request bytes, send them, read response bytes,
deserialize them, and stop there.

## Recommended browser HTTP adapter

This is the default browser integration path.

```ts
import {
  Client,
  ClientOptions,
  Message,
  Serializer,
  TelepactError,
} from 'telepact';

function createTelepactFetchAdapter(
  url: string,
  baseInit: RequestInit = {},
) {
  return async (message: Message, serializer: Serializer): Promise<Message> => {
    const requestBytes = serializer.serialize(message);

    const response = await fetch(url, {
      ...baseInit,
      method: 'POST',
      headers: {
        'Content-Type': 'application/octet-stream',
        ...(baseInit.headers ?? {}),
      },
      body: requestBytes,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status} ${response.statusText}`);
    }

    const responseBytes = new Uint8Array(await response.arrayBuffer());
    return serializer.deserialize(responseBytes);
  };
}

const options = new ClientOptions();
const client = new Client(
  createTelepactFetchAdapter('/api/telepact', {
    credentials: 'include',
  }),
  options,
);

try {
  const response = await client.request(
    new Message({}, { 'fn.greet': { subject: 'World' } }),
  );

  switch (response.getBodyTarget()) {
    case 'Ok_':
      console.log(response.getBodyPayload().message);
      break;
    case 'ErrorUnauthenticated_':
      redirectToLogin();
      break;
    default:
      throw new Error(
        `Unhandled Telepact response: ${JSON.stringify(response.body)}`,
      );
  }
} catch (error) {
  if (error instanceof TelepactError) {
    console.error(error.kind, error.message, error.cause);
  }
  throw error;
}
```

Why this is the recommended shape:

- the adapter owns transport-only concerns such as URL, credentials, and HTTP status handling
- `Client` owns Telepact concerns such as timeout headers, binary negotiation, and serialization
- app code handles schema-level response unions instead of mixing them into transport code

## Request and response handling

Treat Telepact requests and responses as two separate layers:

- **transport failures** raise local exceptions such as `TelepactError` with
  kind `transport` or `serialization`
- **schema-level responses** come back as normal Telepact messages and should be
  handled by switching on `response.getBodyTarget()`

That means:

- use `new Message(headers, { 'fn.someCall': payload })` to issue a request
- use `response.getBodyTarget()` to identify the returned union case
- use `response.getBodyPayload()` after you know which case you received
- keep retry logic, auth refresh, tracing, and metrics at the adapter boundary

## Cookies and auth in browsers

For browser clients:

- do **not** manually set the `Cookie` header in JavaScript
- use `fetch(..., { credentials: 'include' })` when browser cookies should flow
- for cross-origin cookies, configure CORS and cookie policy at the HTTP layer

On the server side, copy transport credentials into Telepact headers at the
transport edge:

```ts
const response = await server.process(requestBytes, (headers) => {
  headers['@auth_'] = { sessionToken: readSessionCookie(request) };
  headers['@id_'] = request.id;
});
```

That keeps browser cookie handling in HTTP where it belongs, while still making
the authenticated caller explicit inside Telepact.

## Binary in browser clients

Recommended rollout:

1. start with the default client options while the endpoint is still being wired
2. once the browser path is stable, turn on binary negotiation
3. keep the transport adapter byte-oriented the whole time

```ts
const options = new ClientOptions();
options.useBinary = true;
options.alwaysSendJson = true;
options.localStorageCacheNamespace = 'greet-api';
```

Notes:

- `useBinary = true` enables negotiated binary
- `alwaysSendJson = true` keeps the request path resilient while encodings are
  learned or refreshed
- `localStorageCacheNamespace` persists negotiated binary encodings in browser
  storage for that API
- once you use `Client`, the adapter should always read and write bytes, not
  `JSON.stringify(...)` / `response.json()`

## Plain JSON vs the TS library vs generated bindings

### Use plain JSON plus `fetch` when you want:

- the fastest possible first request
- browser-devtools or console exploration
- a one-off script or smoke test

### Use the TypeScript library when you want:

- the recommended production browser path
- a stable transport adapter boundary
- easier request/response handling
- negotiated binary without hand-rolling the protocol

### Use generated bindings when you want:

- a typed application-facing client API on top of the TS runtime
- less repeated `Message` construction in app code
- stronger compile-time feedback from a shared schema

The paths are complementary:

- plain JSON is great for first contact
- the TS library should be the team default for browser apps
- generated bindings are the ergonomic layer you add when a schema becomes a
  long-lived contract

## Server adapters use the same cutpoint

TypeScript servers follow the same thin-adapter pattern at the raw byte
boundary.

```ts
import * as fs from 'node:fs';
import * as path from 'node:path';
import {
  FunctionRouter,
  Message,
  Server,
  ServerOptions,
  TelepactSchema,
} from 'telepact';

const schema = TelepactSchema.fromDirectory('/absolute/path/to/api', fs, path);

const functionRouter = new FunctionRouter({
  'fn.greet': async (functionName: string, requestMessage: Message) => {
    const argument = requestMessage.body[functionName] as Record<string, any>;
    return new Message({}, { Ok_: { message: `Hello ${argument.subject}!` } });
  },
});

const options = new ServerOptions();
options.authRequired = false;

const server = new Server(schema, functionRouter, options);

transport.receive(async (requestBytes: Uint8Array) => {
  const response = await server.process(requestBytes);
  return response.bytes;
});
```

## See also

- [Transport Guide](../../doc/03-build-clients-and-servers/01-transports.md)
- [Client Paths](../../doc/03-build-clients-and-servers/02-client-paths.md)
- [Tooling Workflow](../../doc/03-build-clients-and-servers/04-tooling-workflow.md)
- [Runtime Error Guide](../../doc/04-operate/02-runtime-errors.md)
