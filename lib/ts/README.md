# Telepact

## Installation

The library is currently installed directly from the
[Releases](https://github.com/Telepact/telepact/releases) page. You can copy the
link for the library from the release assets.

Example:

```
npm install https://github.com/Telepact/telepact/releases/download/1.0.0-alpha.102/telepact-1.0.0-alpha.102.tgz
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
const files = new TelepactSchemaFiles('/directory/containing/api/files', fs, path);
const schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);

const handler = async (requestMessage: Message): Promise<Message> => {
    const functionName = Object.keys(requestMessage.body)[0];
    const arguments = requestMessage.body[functionName];

    if (functionName == 'fn.greet') {
        var subject = arguments['subject'];
        return new Message({}, {Ok_: {message: `Hello ${subject}!`}});
    }
    
    throw new Error('Function not found');
};

const options = new ServerOptions();
const server = new Server(schema, handler, options);

// Wire up request/response bytes from your transport of choice
const responseBytes = server.process(requestBytes);
```

Client:
```ts
const adapter: (m: Message, s: Serializer) => Promise<Message> = async (m, s) => {
    const requestBytes = s.serialize(m);

    // Wire up request/response bytes to your transport of choice

    return s.deserialize(responseBytes);
};

const options = new ClientOptions();
const client = new Client(adapter, options);
```

For more concrete usage examples, [see the tests](https://github.com/Telepact/telepact/blob/main/test/lib/ts/src/main.ts).
