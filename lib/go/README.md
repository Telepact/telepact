## Telepact Library for Go

### Installation

```bash
go get github.com/telepact/telepact/lib/go@v1.0.0-alpha.162
```

### Usage

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

    handler := func(request telepact.Message) (telepact.Message, error) {
        functionName, err := request.BodyTarget()
        if err != nil {
            return telepact.Message{}, err
        }

        arguments, err := request.BodyPayload()
        if err != nil {
            return telepact.Message{}, err
        }

        // Early in the handler, perform any pre-flight "middleware" operations, such as
        // authentication, tracing, or logging.
        log.Printf("Function started: %s", functionName)
    
        // At the end the handler, perform any post-flight "middleware" operations
        defer log.Printf("Function finished: %s", functionName)

        // Dispatch request to appropriate function handling code.
        // (This example uses manual dispatching, but you can also use a more advanced pattern.)
        if functionName == "fn.greet" {
            subject, _ := arguments["subject"].(string)
            return telepact.NewMessage(
                map[string]any{},
                map[string]any{
                    "Ok_": map[string]any{
                        "message": fmt.Sprintf("Hello %s!", subject),
                    },
                },
            ), nil
        }

        return telepact.Message{}, telepact.NewTelepactError("function not found")
    }

    serverOptions := telepact.NewServerOptions()
    server, err := telepact.NewServer(schema, handler, serverOptions)
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
