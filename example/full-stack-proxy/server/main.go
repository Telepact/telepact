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
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"syscall"
	"time"

	nats "github.com/nats-io/nats.go"
	telepact "github.com/telepact/telepact/lib/go"
)

func main() {
	natsURL := flag.String("nats-url", "nats://127.0.0.1:4222", "NATS server URL")
	subject := flag.String("subject", "rpc.demo.greet", "NATS subject to serve")
	apiDir := flag.String("api-dir", "../api", "Directory containing Telepact schema files")
	healthPort := flag.Int("health-port", 8413, "HTTP health port")
	flag.Parse()

	server, err := buildTelepactServer(*apiDir, *subject)
	if err != nil {
		log.Fatal(err)
	}

	nc, err := nats.Connect(*natsURL, nats.Name("telepact-full-stack-proxy-example"))
	if err != nil {
		log.Fatal(err)
	}
	defer nc.Close()

	_, err = nc.Subscribe(*subject, func(msg *nats.Msg) {
		resp, processErr := server.Process(msg.Data)
		if processErr != nil {
			log.Printf("server.Process error: %v", processErr)
			_ = msg.Respond(buildUnknownPayload())
			return
		}
		if respondErr := msg.Respond(resp.Bytes); respondErr != nil {
			log.Printf("respond error: %v", respondErr)
		}
	})
	if err != nil {
		log.Fatal(err)
	}
	if err := nc.Flush(); err != nil {
		log.Fatal(err)
	}

	healthServer := &http.Server{
		Addr:              fmt.Sprintf("127.0.0.1:%d", *healthPort),
		ReadHeaderTimeout: 5 * time.Second,
		Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if r.URL.Path != "/healthz" {
				http.NotFound(w, r)
				return
			}
			w.Header().Set("Content-Type", "application/json; charset=utf-8")
			_ = json.NewEncoder(w).Encode(map[string]any{
				"ok":      true,
				"subject": *subject,
			})
		}),
	}

	go func() {
		if serveErr := healthServer.ListenAndServe(); serveErr != nil && serveErr != http.ErrServerClosed {
			log.Printf("health server error: %v", serveErr)
		}
	}()

	log.Printf("go proxy example server ready on %s", *subject)

	signals := make(chan os.Signal, 1)
	signal.Notify(signals, syscall.SIGINT, syscall.SIGTERM)
	<-signals

	_ = healthServer.Close()
}

func buildTelepactServer(apiDir string, subject string) (*telepact.Server, error) {
	files, err := telepact.NewTelepactSchemaFiles(filepath.Clean(apiDir))
	if err != nil {
		return nil, err
	}
	schema, err := telepact.TelepactSchemaFromFileJSONMap(files.FilenamesToJSON)
	if err != nil {
		return nil, err
	}

	functionRouter := telepact.NewFunctionRouter(map[string]telepact.FunctionRoute{
		"fn.greet": func(functionName string, requestMessage telepact.Message) (telepact.Message, error) {
			arguments, ok := requestMessage.Body[functionName].(map[string]any)
			if !ok {
				return telepact.Message{}, fmt.Errorf("unexpected %s payload", functionName)
			}
			name, _ := arguments["name"].(string)
			return telepact.NewMessage(
				map[string]any{},
				map[string]any{
					"Ok_": map[string]any{
						"message": fmt.Sprintf("Hello %s from the Go Telepact server!", name),
					},
				},
			), nil
		},
	})

	options := telepact.NewServerOptions()
	return telepact.NewServer(schema, functionRouter, options)
}

func buildUnknownPayload() []byte {
	payload, err := json.Marshal([]any{map[string]any{}, map[string]any{"ErrorUnknown_": map[string]any{}}})
	if err != nil {
		return []byte(`[{},{"ErrorUnknown_":{}}]`)
	}
	return payload
}
