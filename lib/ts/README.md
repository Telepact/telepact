# Telepact Library for TypeScript

## Installation

```
npm install telepact
```

## Usage

API:
```yaml
- fn.greet:
    subject: string
  ->:
    Ok_:
      message: string
```

Server:
```ts
import * as fs from 'fs';
import * as path from 'path';
import { FunctionRouter, Message, Server, ServerOptions, TelepactSchema, TelepactSchemaFiles } from 'telepact';

const files = new TelepactSchemaFiles('/directory/containing/api/files', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);

// The schema directory may contain multiple *.telepact.yaml and
// *.telepact.json files. Subdirectories are rejected.

const functionRoutes = {
    'fn.greet': async (functionName: string, requestMessage: Message): Promise<Message> => {
        const argument = requestMessage.body[functionName] as Record<string, any>;
        const subject = argument['subject'];
        return new Message({}, {Ok_: {message: `Hello ${subject}!`}});
    },
};

const options = new ServerOptions();
// Set this to false when your schema does not define union.Auth_.
options.authRequired = false;
options.middleware = async (requestMessage: Message, functionRouter): Promise<Message> => {
    const functionName = requestMessage.getBodyTarget();
    try {
        log.info("Function started", {function: functionName});
        return await functionRouter.route(requestMessage);
    } finally {
        log.info("Function finished", {function: functionName});
    }
};
const functionRouter = new FunctionRouter(functionRoutes);
const server = new Server(schema, functionRouter, options);

// Wire up request/response bytes from your transport of choice
transport.receive(async (requestBytes: Uint8Array): Promise<Uint8Array> => {
    const response = await server.process(requestBytes);
    return response.bytes;
});
```

Client:
```ts
import { Client, ClientOptions, Message, Serializer } from 'telepact';

const adapter: (m: Message, s: Serializer) => Promise<Message> = async (m, s) => {
    const requestBytes = s.serialize(m);

    // Wire up request/response bytes to your transport of choice
    const responseBytes = await transport.send(requestBytes);

    return s.deserialize(responseBytes);
};

const options = new ClientOptions();
const client = new Client(adapter, options);

// Inside an async function in your application:
const request = new Message({}, { 'fn.greet': { subject: 'World' } });
const response = await client.request(request);
if (response.getBodyTarget() === 'Ok_') {
    const okPayload = response.getBodyPayload();
    console.log(okPayload.message);
} else {
    throw new Error(`Unexpected response: ${JSON.stringify(response.body)}`);
}
```

For browser + Node paths, start with:

- [Client Paths](../../doc/03-build-clients-and-servers/02-client-paths.md)
- [Transport Guide](../../doc/03-build-clients-and-servers/01-transports.md)
- [Demos](../../doc/demos.md)

For generated TypeScript bindings, see:

- [Tooling Workflow](../../doc/03-build-clients-and-servers/04-tooling-workflow.md)
- [Learn by Example: Code generation](../../doc/01-learn-by-example/07-code-generation/21-code-generation.md)

The TypeScript tests also contain lower-level examples:
[test/lib/ts/src/main.ts](../../test/lib/ts/src/main.ts).
