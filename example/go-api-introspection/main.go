//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package main

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"

	telepact "github.com/telepact/telepact/lib/go"
)

func main() {
	if len(os.Args) < 3 {
		log.Fatal("usage: go run . server <port> | go run . check <url>")
	}

	switch os.Args[1] {
	case "server":
		port, err := strconv.Atoi(os.Args[2])
		if err != nil {
			log.Fatal(err)
		}
		runServer(port)
	case "check":
		runCheck(os.Args[2])
	default:
		log.Fatalf("unknown mode: %s", os.Args[1])
	}
}

func buildServer() (*telepact.Server, error) {
	files, err := telepact.NewTelepactSchemaFiles("api")
	if err != nil {
		return nil, err
	}

	schema, err := telepact.TelepactSchemaFromFileJSONMap(files.FilenamesToJSON)
	if err != nil {
		return nil, err
	}

	options := telepact.NewServerOptions()
	options.AuthRequired = false

	return telepact.NewServer(schema, func(request telepact.Message) (telepact.Message, error) {
		functionName, err := request.BodyTarget()
		if err != nil {
			return telepact.Message{}, err
		}
		if functionName != "fn.ping" {
			return telepact.Message{}, fmt.Errorf("unknown function: %s", functionName)
		}
		return telepact.NewMessage(map[string]any{}, map[string]any{
			"Ok_": map[string]any{"pong": "pong"},
		}), nil
	}, options)
}

func runServer(port int) {
	server, err := buildServer()
	if err != nil {
		log.Fatal(err)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(writer http.ResponseWriter, request *http.Request) {
		writer.WriteHeader(http.StatusOK)
		_, _ = writer.Write([]byte("ok"))
	})
	mux.HandleFunc("/api/telepact", func(writer http.ResponseWriter, request *http.Request) {
		if request.Method != http.MethodPost {
			writer.WriteHeader(http.StatusMethodNotAllowed)
			return
		}
		requestBytes, err := io.ReadAll(request.Body)
		if err != nil {
			writer.WriteHeader(http.StatusInternalServerError)
			_, _ = writer.Write([]byte(err.Error()))
			return
		}
		response, err := server.Process(requestBytes)
		if err != nil {
			writer.WriteHeader(http.StatusInternalServerError)
			_, _ = writer.Write([]byte(err.Error()))
			return
		}
		contentType := "application/json"
		if _, ok := response.Headers["@bin_"]; ok {
			contentType = "application/octet-stream"
		}
		writer.Header().Set("Content-Type", contentType)
		writer.WriteHeader(http.StatusOK)
		_, _ = writer.Write(response.Bytes)
	})

	address := fmt.Sprintf("127.0.0.1:%d", port)
	log.Printf("go-api-introspection listening on http://%s", address)
	log.Fatal(http.ListenAndServe(address, mux))
}

func runCheck(url string) {
	adapter := func(ctx context.Context, request telepact.Message, serializer *telepact.Serializer) (telepact.Message, error) {
		requestBytes, err := serializer.Serialize(request)
		if err != nil {
			return telepact.Message{}, err
		}

		httpRequest, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(requestBytes))
		if err != nil {
			return telepact.Message{}, err
		}
		httpRequest.Header.Set("Content-Type", "application/json")

		response, err := http.DefaultClient.Do(httpRequest)
		if err != nil {
			return telepact.Message{}, err
		}
		defer response.Body.Close()

		responseBytes := mustReadAll(response)
		return serializer.Deserialize(responseBytes)
	}

	client, err := telepact.NewClient(adapter, telepact.NewClientOptions())
	if err != nil {
		log.Fatal(err)
	}

	pingResponse, err := client.Request(telepact.NewMessage(map[string]any{}, map[string]any{"fn.ping": map[string]any{}}))
	if err != nil {
		log.Fatal(err)
	}
	if pingResponse.Body["Ok_"] == nil {
		log.Fatalf("unexpected ping response: %+v", pingResponse.Body)
	}

	apiResponse, err := client.Request(telepact.NewMessage(map[string]any{}, map[string]any{"fn.api_": map[string]any{}}))
	if err != nil {
		log.Fatal(err)
	}
	apiPayload, ok := apiResponse.Body["Ok_"].(map[string]any)
	if !ok {
		log.Fatalf("unexpected api response: %+v", apiResponse.Body)
	}
	apiList, ok := apiPayload["api"].([]any)
	if !ok {
		log.Fatalf("unexpected api payload: %+v", apiPayload)
	}
	foundPing := false
	for _, entry := range apiList {
		if definition, ok := entry.(map[string]any); ok {
			if _, ok := definition["fn.ping"]; ok {
				foundPing = true
				break
			}
		}
	}
	if !foundPing {
		log.Fatalf("fn.ping not found in fn.api_ response: %+v", apiPayload)
	}

	fmt.Println("go-api-introspection check passed")
}

func mustReadAll(response *http.Response) []byte {
	data, err := io.ReadAll(response.Body)
	if err != nil {
		log.Fatal(err)
	}
	return data
}
