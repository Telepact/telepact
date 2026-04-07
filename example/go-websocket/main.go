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
	"net/http"

	"github.com/gorilla/websocket"
	telepact "github.com/telepact/telepact/lib/go"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
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
	options.Middleware = func(headers map[string]any, functionName string, arguments map[string]any, next telepact.ServerNext) (telepact.Message, error) {
		if functionName != "fn.greet" {
			return telepact.Message{}, fmt.Errorf("unknown function: %s", functionName)
		}

		subject, _ := arguments["subject"].(string)
		return telepact.NewMessage(map[string]any{}, map[string]any{
			"Ok_": map[string]any{
			"message": fmt.Sprintf("Hello %s from WebSocket!", subject),
			},
		}), nil
	}
	return telepact.NewServer(schema, options)
}

func newWebsocketHandler() (http.Handler, error) {
	server, err := buildServer()
	if err != nil {
		return nil, err
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/ws/telepact", func(writer http.ResponseWriter, request *http.Request) {
		conn, err := upgrader.Upgrade(writer, request, nil)
		if err != nil {
			return
		}
		defer conn.Close()

		for {
			messageType, requestBytes, err := conn.ReadMessage()
			if err != nil {
				return
			}

			response, err := server.Process(requestBytes)
			if err != nil {
				return
			}

			if messageType == websocket.TextMessage {
				err = conn.WriteMessage(websocket.TextMessage, response.Bytes)
			} else {
				err = conn.WriteMessage(websocket.BinaryMessage, response.Bytes)
			}
			if err != nil {
				return
			}
		}
	})

	return mux, nil
}
