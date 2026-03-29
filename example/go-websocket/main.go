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
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/gorilla/websocket"
	telepact "github.com/telepact/telepact/lib/go"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
}

func main() {
	if len(os.Args) < 3 {
		log.Fatal("usage: go run . server <port> | go run . check <ws-url>")
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

		arguments, err := request.BodyPayload()
		if err != nil {
			return telepact.Message{}, err
		}

		if functionName != "fn.greet" {
			return telepact.Message{}, fmt.Errorf("unknown function: %s", functionName)
		}

		subject, _ := arguments["subject"].(string)
		return telepact.NewMessage(map[string]any{}, map[string]any{
			"Ok_": map[string]any{
				"message": fmt.Sprintf("Hello %s from WebSocket!", subject),
			},
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
				log.Println(err)
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

	address := fmt.Sprintf("127.0.0.1:%d", port)
	log.Printf("go-websocket listening on ws://%s/ws/telepact", address)
	log.Fatal(http.ListenAndServe(address, mux))
}

func runCheck(wsURL string) {
	conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()

	request := `[{}, {"fn.greet": {"subject": "Telepact"}}]`
	if err := conn.WriteMessage(websocket.TextMessage, []byte(request)); err != nil {
		log.Fatal(err)
	}

	_, responseBytes, err := conn.ReadMessage()
	if err != nil {
		log.Fatal(err)
	}

	response := string(responseBytes)
	if !strings.Contains(response, "Hello Telepact from WebSocket!") {
		log.Fatalf("unexpected response: %s", response)
	}

	fmt.Println("go-websocket check passed")
}
