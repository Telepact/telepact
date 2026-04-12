// First generate bindings from the schema:
// telepact codegen --schema-dir ./api --lang go --package calcclient --out ./gen

package main

import (
    "context"
    "log"

    calcclient "example.com/project/gen"
    telepact "github.com/telepact/telepact/lib/go"
)

func main() {
    adapter := func(ctx context.Context, request telepact.Message, serializer *telepact.Serializer) (telepact.Message, error) {
        requestBytes, err := serializer.Serialize(request)
        if err != nil {
            return telepact.Message{}, err
        }

        responseBytes, err := transport.Send(ctx, requestBytes)
        if err != nil {
            return telepact.Message{}, err
        }

        return serializer.Deserialize(responseBytes)
    }

    client, err := calcclient.NewClient(adapter, telepact.NewClientOptions())
    if err != nil {
        log.Fatal(err)
    }

    response, err := client.Divide(context.Background(), calcclient.FnDivideArgs{
        X: 10,
        Y: 2,
    })
    if err != nil {
        log.Fatal(err)
    }

    log.Printf("result=%v", response.Ok.Result)
}
