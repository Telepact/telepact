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
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/gorilla/websocket"
)

func TestWebsocketExample(t *testing.T) {
	handler, err := newWebsocketHandler()
	if err != nil {
		t.Fatal(err)
	}

	server := httptest.NewServer(handler)
	defer server.Close()
	wsURL := strings.Replace(server.URL, "http://", "ws://", 1) + "/ws/telepact"

	conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	if err != nil {
		t.Fatal(err)
	}
	defer conn.Close()

	request := `[{}, {"fn.greet": {"subject": "Telepact"}}]`
	if err := conn.WriteMessage(websocket.TextMessage, []byte(request)); err != nil {
		t.Fatal(err)
	}

	_, responseBytes, err := conn.ReadMessage()
	if err != nil {
		t.Fatal(err)
	}

	response := string(responseBytes)
	if !strings.Contains(response, "Hello Telepact from WebSocket!") {
		t.Fatalf("unexpected response: %s", response)
	}
}
