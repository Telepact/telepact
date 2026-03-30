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
	"net/http"
	"net/http/httptest"
	"testing"

	telepact "github.com/telepact/telepact/lib/go"
)

func TestAPIIntrospectionExample(t *testing.T) {
	handler, err := newHTTPHandler()
	if err != nil {
		t.Fatal(err)
	}

	server := httptest.NewServer(handler)
	defer server.Close()
	url := server.URL + "/api/telepact"

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
		t.Fatal(err)
	}

	pingResponse, err := client.Request(telepact.NewMessage(map[string]any{}, map[string]any{"fn.ping": map[string]any{}}))
	if err != nil {
		t.Fatal(err)
	}
	if pingResponse.Body["Ok_"] == nil {
		t.Fatalf("unexpected ping response: %+v", pingResponse.Body)
	}

	apiResponse, err := client.Request(telepact.NewMessage(map[string]any{}, map[string]any{"fn.api_": map[string]any{}}))
	if err != nil {
		t.Fatal(err)
	}
	apiPayload, ok := apiResponse.Body["Ok_"].(map[string]any)
	if !ok {
		t.Fatalf("unexpected api response: %+v", apiResponse.Body)
	}
	apiList, ok := apiPayload["api"].([]any)
	if !ok {
		t.Fatalf("unexpected api payload: %+v", apiPayload)
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
		t.Fatalf("fn.ping not found in fn.api_ response: %+v", apiPayload)
	}
}
