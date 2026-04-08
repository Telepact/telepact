## Telepact Library for Go

### Installation

```bash
go get github.com/telepact/telepact/lib/go
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
            arguments, _ := requestMessage.Body[functionName].(map[string]any)
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
	serverOptions.AuthRequired = false
	serverOptions.Middleware = func(request telepact.Message, functionRouter *telepact.FunctionRouter) (telepact.Message, error) {
        functionName, err := request.BodyTarget()
        if err != nil {
            return telepact.Message{}, err
        }
        log.Printf("Function started: %s", functionName)
        defer log.Printf("Function finished: %s", functionName)
        return functionRouter.Route(request)
    }
	server, err := telepact.NewServer(schema, functionRoutes, serverOptions)
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
