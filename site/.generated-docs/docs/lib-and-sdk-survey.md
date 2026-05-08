# Lib and SDK Survey

## Go

#### Installation

```bash
go get github.com/telepact/telepact/lib/go
```

#### Usage

API:

```yaml
- fn.greet:
    subject: string
  ->:
    Ok_:
      message: string
```

Server:

```go
package main

import (
    "fmt"
    "log"

    telepact "github.com/telepact/telepact/lib/go"
)

func main() {
    files, err := telepact.NewTelepactSchemaFiles("./directory/containing/api/files")
    if err != nil {
        log.Fatal(err)
    }

    schema, err := telepact.TelepactSchemaFromFileJSONMap(files.FilenamesToJSON)
    if err != nil {
        log.Fatal(err)
    }

    // The schema directory may contain multiple *.telepact.yaml and
    // *.telepact.json files. Subdirectories are rejected.

    functionRoutes := map[string]telepact.FunctionRoute{
        "fn.greet": func(functionName string, requestMessage telepact.Message) (telepact.Message, error) {
            arguments, ok := requestMessage.Body[functionName].(map[string]any)
            if !ok {
                return telepact.Message{}, fmt.Errorf("unexpected %s payload", functionName)
            }
            subject, _ := arguments["subject"].(string)
            return telepact.NewMessage(
                map[string]any{},
                map[string]any{
                    "Ok_": map[string]any{
                        "message": fmt.Sprintf("Hello %s!", subject),
                    },
                },
            ), nil
        },
    }

	serverOptions := telepact.NewServerOptions()
	// Set this to false when your schema does not define union.Auth_.
	serverOptions.Middleware = func(request telepact.Message, functionRouter *telepact.FunctionRouter) (telepact.Message, error) {
        functionName, err := request.BodyTarget()
        if err != nil {
            return telepact.Message{}, err
        }
        log.Printf("Function started: %s", functionName)
        defer log.Printf("Function finished: %s", functionName)
        return functionRouter.Route(request)
    }
	functionRouter := telepact.NewFunctionRouter()
	functionRouter.RegisterUnauthenticatedRoutes(functionRoutes)
	server, err := telepact.NewServer(schema, functionRouter, serverOptions)
	if err != nil {
		log.Fatal(err)
    }

    // Wire up request/response bytes from your transport of choice
    transport.Receive(func(requestBytes []byte) ([]byte, error) {
        response, err := server.Process(requestBytes)
        if err != nil {
            return nil, err
        }
        return response.Bytes, nil
    })
}
```

Client:

```go
package main

import (
    "context"
    "log"

    telepact "github.com/telepact/telepact/lib/go"
)

func main() {
    adapter := func(ctx context.Context, request telepact.Message, serializer *telepact.Serializer) (telepact.Message, error) {
        requestBytes, err := serializer.Serialize(request)
        if err != nil {
            return telepact.Message{}, err
        }

        // Wire up request/response bytes to your transport of choice
        responseBytes, err := transport.Send(ctx, requestBytes)
        if err != nil {
            return telepact.Message{}, err
        }

        return serializer.Deserialize(responseBytes)
    }

    clientOptions := telepact.NewClientOptions()
    client, err := telepact.NewClient(adapter, clientOptions)
    if err != nil {
        log.Fatal(err)
    }

    response, err := client.Request(
        telepact.NewMessage(
            map[string]any{},
            map[string]any{
                "fn.greet": map[string]any{"subject": "Telepact"},
            },
        ),
    )
    if err != nil {
        log.Fatal(err)
    }

    log.Printf("Response: %+v", response)
}
```

For more concrete usage examples, [see the tests](https://github.com/Telepact/telepact/tree/main/test/lib/go).

## Java

#### Java version

Requires **Java 21**.

#### Installation
```xml
<dependency>
    <groupId>io.github.telepact</groupId>
    <artifactId>telepact</artifactId>
</dependency>
```

#### Usage

API:
```yaml
- fn.greet:
    subject: string
  ->:
    Ok_:
      message: string
```

Server:
```java
import io.github.telepact.Client;
import io.github.telepact.FunctionRoute;
import io.github.telepact.FunctionRouter;
import io.github.telepact.Message;
import io.github.telepact.Serializer;
import io.github.telepact.Server;
import io.github.telepact.TelepactSchema;
import io.github.telepact.TelepactSchemaFiles;

var files = new TelepactSchemaFiles("./directory/containing/api/files");
var schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
// The schema directory may contain multiple *.telepact.yaml and
// *.telepact.json files. Subdirectories are rejected.
Map<String, FunctionRoute> functionRoutes = Map.of(
    "fn.greet",
    (functionName, requestMessage) -> {
        var arguments = (Map<String, Object>) requestMessage.body.get(functionName);
        var subject = (String) arguments.get("subject");
        return new Message(Map.of(), Map.of("Ok_", Map.of("message", "Hello %s!".formatted(subject))));
    }
);
var options = new Server.Options();
// Set this to false when your schema does not define union.Auth_.
options.middleware = (requestMessage, functionRouter) -> {
    var functionName = requestMessage.getBodyTarget();
    try {
        log.info("Function started", Map.of("function", functionName));
        return functionRouter.route(requestMessage);
    } finally {
        log.info("Function finished", Map.of("function", functionName));
    }
};
var functionRouter = new FunctionRouter();
functionRouter.registerUnauthenticatedRoutes(functionRoutes);
var server = new Server(schema, functionRouter, options);


// Wire up request/response bytes from your transport of choice
transport.receive((requestBytes) -> {
    var response = server.process(requestBytes);
    return response.bytes;
});
```

Client:
```java
BiFunction<Message, Serializer, Future<Message>> adapter = (m, s) -> {
    return CompletableFuture.supplyAsync(() -> {
        var requestBytes = s.serialize(m);
        
        // Wire up request/response bytes to your transport of choice
        var responseBytes = transport.send(requestBytes);
        
        return s.deserialize(responseBytes);
    });
};
var options = new Client.Options();
var client = new Client(adapter, options);

var request = new Message(
    Map.of(),
    Map.of("fn.greet", Map.of("subject", "World"))
);
var response = client.request(request);
if ("Ok_".equals(response.getBodyTarget())) {
    var okPayload = response.getBodyPayload();
    System.out.println(okPayload.get("message"));
} else {
    throw new RuntimeException("Unexpected response: " + response.body);
}
```

For more concrete usage examples, [see the tests](https://github.com/Telepact/telepact/blob/main/test/lib/java/src/main/java/telepacttest/Main.java).

## Python

#### Installation

```
pip install --pre telepact
```

#### Usage

API:

```yaml
- fn.greet:
    subject: string
  ->:
    Ok_:
      message: string
```

Server:

```py
from telepact import Client, FunctionRouter, Message, Serializer, Server, TelepactSchema

schema = TelepactSchema.from_directory('/directory/containing/api/files')

# The schema directory may contain multiple *.telepact.yaml and
# *.telepact.json files. Subdirectories are rejected.

async def greet(function_name: str, request_message: 'Message') -> 'Message':
    arguments = request_message.body[function_name]
    subject = arguments['subject']
    return Message({}, {'Ok_': {'message': f'Hello {subject}!'}})


async def middleware(request_message: 'Message', function_router) -> 'Message':
    function_name = request_message.get_body_target()
    try:
        log.info("Function started", {'function': function_name})
        return await function_router.route(request_message)
    finally:
        log.info("Function finished", {'function': function_name})


options = Server.Options()
# Set this to False when your schema does not define union.Auth_.
options.middleware = middleware
function_router = FunctionRouter()
function_router.register_unauthenticated_routes({'fn.greet': greet})
server = Server(schema, function_router, options)


# Wire up request/response bytes from your transport of choice
async def transport_handler(request_bytes: bytes) -> bytes:
    response = await server.process(request_bytes)
    return response.bytes

transport.receive(transport_handler)
```

Client:

```py
async def adapter(m: Message, s: Serializer) -> Message:
    request_bytes = s.serialize(m)

    # Wire up request/response bytes to your transport of choice
    response_bytes = await transport.send(request_bytes)

    return s.deserialize(response_bytes)

options = Client.Options()
client = Client(adapter, options)

# Inside your async application code:
request = Message({}, {'fn.greet': {'subject': 'World'}})
response = await client.request(request)
if response.get_body_target() == 'Ok_':
    ok_payload = response.get_body_payload()
    print(ok_payload['message'])
else:
    raise RuntimeError(f"Unexpected response: {response.body}")
```

For more concrete usage examples,
[see the tests](https://github.com/Telepact/telepact/blob/main/test/lib/py/telepact_test/test_server.py).

## TypeScript

### Installation

```
npm install telepact
```

### Usage

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
options.middleware = async (requestMessage: Message, functionRouter): Promise<Message> => {
    const functionName = requestMessage.getBodyTarget();
    try {
        log.info("Function started", {function: functionName});
        return await functionRouter.route(requestMessage);
    } finally {
        log.info("Function finished", {function: functionName});
    }
};
const functionRouter = new FunctionRouter();
functionRouter.registerUnauthenticatedRoutes(functionRoutes);
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

### See also

- [Transport Guide](concepts.md#transport-guide) for browser TypeScript + `fetch` and WebSocket examples
- [Client Paths](concepts.md#client-paths) for choosing between plain JSON, the runtime library, and generated code
- [Demos](examples.md) for runnable end-to-end examples

## CLI

The CLI is a tool for various development jobs, such as fetching API schemas,
starting schema-backed mock servers for testing purposes, and optionally
generating code.

### Installation

```
uv tool install --prerelease=allow telepact-cli
```

### Usage

#### `telepact --help`
```
Usage: telepact [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  codegen      Generate code bindings for a Telepact API schema.
  compare      Compare two Telepact API schemas for backwards compatibility.
  demo-server  Start a demo Telepact server.
  fetch        Fetch a Telepact API schema to store locally.
  mock         Start a mock server for a Telepact API schema.
```

#### `telepact codegen --help`
```
Usage: telepact codegen [OPTIONS]

  Generate code bindings for a Telepact API schema.

Options:
  --schema-http-url TEXT  telepact schema directory
  --schema-dir TEXT       telepact schema directory
  --lang TEXT             Language target (one of "java", "py", "ts", or "go")
                          [required]
  --out TEXT              Output directory  [required]
  --package TEXT          Package name (required when --lang is "java" or "go")
  --help                  Show this message and exit.
```

#### `telepact compare --help`
```
Usage: telepact compare [OPTIONS]

  Compare two Telepact API schemas for backwards compatibility.

Options:
  --new-schema-dir TEXT  New telepact schema directory  [required]
  --old-schema-dir TEXT  Old telepact schema directory  [required]
  --help                 Show this message and exit.
```

#### `telepact fetch --help`
```
Usage: telepact fetch [OPTIONS]

  Fetch a Telepact API schema to store locally.

Options:
  --http-url TEXT    HTTP URL of a Telepact API  [required]
  --output-dir TEXT  Directory of Telepact schemas  [required]
  --help             Show this message and exit.
```

#### `telepact mock --help`
```
Usage: telepact mock [OPTIONS]

  Start a mock server for a Telepact API schema.

Options:
  --http-url TEXT                 HTTP URL of a Telepact API
  --dir TEXT                      Directory of Telepact schemas
  --port INTEGER                  Port to run the mock server on
  --path TEXT                     Path to expose the mock API (default: /api)
  --generated-collection-length-min INTEGER
                                  Minimum length of generated collections
  --generated-collection-length-max INTEGER
                                  Maximum length of generated collections
  --disable-optional-field-generation
                                  Disable generation of optional fields
                                  (enabled by default)
  --disable-message-response-generation
                                  Disable generation of message responses
                                  (enabled by default)
  --disable-random-optional-field-generation
                                  Disable randomization of optional field
                                  generation (enabled by default)
  --help                          Show this message and exit.
```

NOTE: The `mock` command is an empowering development tool for clients. You do
not need to develop against a live server; you can use the `mock` command to
set up a "middle-man" server that will validate requests for schema compliance
and return schema-compliant auto-generated responses (which can be overridden
with manual stubs if desired.)

## Console

The Console is a debugging tool that allows you to easily connect to your
running Telepact server, visualize your API with interactive documentation, and
submit live requests to your server.

### Installation

```
npm install -g telepact-console
```

### Usage

```
npx telepact-console -p 8080
```

Then you can access the UI in your browser at http://localhost:8080.

When launched through the npm CLI, the Console proxies absolute live HTTP and
WebSocket URLs through its own localhost server first while keeping the
self-hosted build unchanged for same-domain embeds.

### Docker

The Console is also available as a docker image, which can be installed directly
from [Releases](https://github.com/Telepact/telepact/releases). You can copy the
link for the Console from the release assets.

Example:

```
curl -L -o telepact-docker.tar.gz https://github.com/Telepact/telepact/releases/download/{version}/docker-image-telepact-console-{version}.tar.gz
docker load < telepact-docker.tar.gz
```

Starting the docker container:

```
docker run -p 8080:8080 telepact-console:{version}
```

For a more concrete usage example, see
[self-hosting example](https://github.com/Telepact/telepact/blob/main/test/console-self-hosted/).

## Prettier Plugin

Formats `.telepact.yaml` and `.telepact.yml` schema files to match the checked-in
Telepact schema style:

- `///` docstrings are emitted as YAML `|` block scalars
- Telepact field values stay in inline JSON form

### Installation

```sh
npm install prettier-plugin-telepact
```

### Usage

Add the plugin to your Prettier config:

```json
{
    "plugins": ["prettier-plugin-telepact"]
}
```
