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

package telepact

import (
	"encoding/json"
	"fmt"

	"github.com/telepact/telepact/lib/go/internal/mock"
	"github.com/telepact/telepact/lib/go/internal/types"
)

// TestClientOptions configures the pseudo-random generation performed by TestClient.
type TestClientOptions struct {
	GeneratedCollectionLengthMin int
	GeneratedCollectionLengthMax int
}

// TestClient exercises a Telepact client, providing helpers for assertion and mock data generation.
type TestClient struct {
	client *Client
	random *RandomGenerator
	schema *TelepactSchema
}

// NewTestClient constructs a TestClient using the supplied Telepact client and options.
func NewTestClient(client *Client, options TestClientOptions) *TestClient {
	generator := NewRandomGenerator(options.GeneratedCollectionLengthMin, options.GeneratedCollectionLengthMax)
	return &TestClient{
		client: client,
		random: generator,
		schema: nil,
	}
}

// AssertRequest issues the provided request and compares the response body against the expected pseudo JSON structure.
func (tc *TestClient) AssertRequest(request Message, expectedPseudoJSONBody map[string]any, expectMatch bool) (Message, error) {
	if tc == nil {
		return Message{}, fmt.Errorf("test client is nil")
	}

	if tc.schema == nil {
		schema, err := tc.fetchSchema()
		if err != nil {
			return Message{}, err
		}
		tc.schema = schema
	}

	responseMessage, err := tc.client.Request(request)
	if err != nil {
		return Message{}, err
	}

	didMatch := mock.IsSubMap(expectedPseudoJSONBody, responseMessage.Body)

	if expectMatch {
		if !didMatch {
			return Message{}, fmt.Errorf("Expected response body was not a sub map. Expected: %v Actual: %v", expectedPseudoJSONBody, responseMessage.Body)
		}
		return responseMessage, nil
	}

	if didMatch {
		return Message{}, fmt.Errorf("Expected response body was a sub map. Expected: %v Actual: %v", expectedPseudoJSONBody, responseMessage.Body)
	}

	useBlueprintValue := true
	includeOptionalFields := false
	alwaysIncludeRequiredFields := true
	randomizeOptionalFieldGeneration := false

	functionName, err := request.BodyTarget()
	if err != nil {
		return Message{}, err
	}

	definitionRaw, ok := tc.schema.Parsed[fmt.Sprintf("%s.->", functionName)]
	if !ok {
		return Message{}, fmt.Errorf("result union type not found for function %s", functionName)
	}

	definition, ok := definitionRaw.(*types.TUnion)
	if !ok {
		return Message{}, fmt.Errorf("result type for %s is not a union", functionName)
	}

	ctx := types.NewGenerateContext(
		includeOptionalFields,
		randomizeOptionalFieldGeneration,
		alwaysIncludeRequiredFields,
		functionName,
		tc.random,
	)

	generatedResult := definition.GenerateRandomValue(
		expectedPseudoJSONBody,
		useBlueprintValue,
		nil,
		ctx,
	)

	resultBody, err := toStringAnyMap(generatedResult)
	if err != nil {
		return Message{}, err
	}

	return NewMessage(responseMessage.Headers, resultBody), nil
}

// SetSeed configures the pseudo-random generator seed.
func (tc *TestClient) SetSeed(seed int32) {
	if tc == nil {
		return
	}
	tc.random.SetSeed(seed)
}

func (tc *TestClient) fetchSchema() (*TelepactSchema, error) {
	response, err := tc.client.Request(NewMessage(map[string]any{}, map[string]any{"fn.api_": map[string]any{}}))
	if err != nil {
		return nil, err
	}

	topLevel, ok := response.Body["Ok_"].(map[string]any)
	if !ok {
		return nil, fmt.Errorf("expected Ok_ response body when fetching schema")
	}

	api := topLevel["api"]
	encoded, err := json.Marshal(api)
	if err != nil {
		return nil, err
	}

	schema, err := TelepactSchemaFromJSON(string(encoded))
	if err != nil {
		return nil, err
	}

	return schema, nil
}

func toStringAnyMap(value any) (map[string]any, error) {
	switch typed := value.(type) {
	case map[string]any:
		return typed, nil
	case map[any]any:
		converted := make(map[string]any, len(typed))
		for k, v := range typed {
			converted[fmt.Sprint(k)] = v
		}
		return converted, nil
	default:
		return nil, fmt.Errorf("expected map result, received %T", value)
	}
}
