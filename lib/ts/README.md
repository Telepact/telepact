# Telepact Library for TypeScript

## Installation

```
npm install --ignore-scripts telepact
```

## Usage

API:
```json
[
    {
        "fn.greet": {
            "subject": "string"
        },
        "->": {
            "Ok_": {
                "message": "string"
            }
        }
    }
]
```

Server:
```ts
import * as fs from 'fs';
import * as path from 'path';

const files = new TelepactSchemaFiles('/directory/containing/api/files', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);

const handler = async (requestMessage: Message): Promise<Message> => {
    const functionName = Object.keys(requestMessage.body)[0];
    const arguments = requestMessage.body[functionName];

    try {
        // Early in the handler, perform any pre-flight "middleware" operations, such as
        // authentication, tracing, or logging.
        log.info("Function started", {function: functionName});

        // Dispatch request to appropriate function handling code.
        // (This example uses manual dispatching, but you can also use a more advanced pattern.)
        if (functionName == 'fn.greet') {
            var subject = arguments['subject'];
            return new Message({}, {Ok_: {message: `Hello ${subject}!`}});
        }

        throw new Error('Function not found');
    } finally {
        // At the end the handler, perform any post-flight "middleware" operations
        log.info("Function finished", {function: functionName});
    }
};

const options = new ServerOptions();
const server = new Server(schema, handler, options);

// Wire up request/response bytes from your transport of choice
transport.receive(async (requestBytes): Promise<Message> => {
    const response = await server.process(requestBytes);
    return response.bytes;
});
```

Client:
```ts
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

For more concrete usage examples, [see the tests](https://github.com/Telepact/telepact/blob/main/test/lib/ts/src/main.ts).
