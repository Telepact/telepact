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
	"fmt"
	"io"
	"net/http"

	telepact "github.com/telepact/telepact/lib/go"
)

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

func newHTTPHandler() (http.Handler, error) {
	server, err := buildServer()
	if err != nil {
		return nil, err
	}

	mux := http.NewServeMux()
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
	return mux, nil
}

func mustReadAll(response *http.Response) []byte {
	data, err := io.ReadAll(response.Body)
	if err != nil {
		panic(err)
	}
	return data
}
