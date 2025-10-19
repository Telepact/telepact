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
	"github.com/telepact/telepact/lib/go/telepact/internal/mock"
)

// MockServerOptions configures behaviour of the mock server.
type MockServerOptions struct {
	OnError                          func(error)
	EnableMessageResponseGeneration  bool
	EnableOptionalFieldGeneration    bool
	RandomizeOptionalFieldGeneration bool
	GeneratedCollectionLengthMin     int
	GeneratedCollectionLengthMax     int
}

// NewMockServerOptions constructs MockServerOptions populated with defaults.
func NewMockServerOptions() *MockServerOptions {
	return &MockServerOptions{
		OnError:                          func(error) {},
		EnableMessageResponseGeneration:  true,
		EnableOptionalFieldGeneration:    true,
		RandomizeOptionalFieldGeneration: true,
		GeneratedCollectionLengthMin:     0,
		GeneratedCollectionLengthMax:     3,
	}
}

// MockServer provides a mock Telepact server implementation.
type MockServer struct {
	random                           *RandomGenerator
	enableGeneratedDefaultStub       bool
	enableOptionalFieldGeneration    bool
	randomizeOptionalFieldGeneration bool
	stubs                            []*mock.MockStub
	invocations                      []*mock.MockInvocation
	server                           *Server
}

// NewMockServer constructs a new MockServer using the supplied schema and options.
func NewMockServer(mockSchema *MockTelepactSchema, options *MockServerOptions) (*MockServer, error) {
	if mockSchema == nil {
		return nil, NewTelepactError("telepact: mock schema must not be nil")
	}

	if options == nil {
		options = NewMockServerOptions()
	}

	if options.OnError == nil {
		options.OnError = func(error) {}
	}

	ms := &MockServer{
		random:                           NewRandomGenerator(options.GeneratedCollectionLengthMin, options.GeneratedCollectionLengthMax),
		enableGeneratedDefaultStub:       options.EnableMessageResponseGeneration,
		enableOptionalFieldGeneration:    options.EnableOptionalFieldGeneration,
		randomizeOptionalFieldGeneration: options.RandomizeOptionalFieldGeneration,
		stubs:                            []*mock.MockStub{},
		invocations:                      []*mock.MockInvocation{},
	}

	serverOptions := NewServerOptions()
	serverOptions.OnError = options.OnError
	serverOptions.AuthRequired = false

	telepactSchema := NewTelepactSchema(
		mockSchema.Original,
		mockSchema.Parsed,
		mockSchema.ParsedRequestHeaders,
		mockSchema.ParsedResponseHeaders,
	)

	server, err := NewServer(telepactSchema, ms.handle, serverOptions)
	if err != nil {
		return nil, err
	}

	ms.server = server

	return ms, nil
}

// Process processes a Telepact request message and returns the serialized response.
func (ms *MockServer) Process(message []byte) (Response, error) {
	if ms == nil || ms.server == nil {
		return Response{}, NewTelepactError("telepact: mock server is not initialized")
	}
	return ms.server.Process(message)
}

func (ms *MockServer) handle(request Message) (Message, error) {
	if ms == nil {
		return Message{}, NewTelepactError("telepact: mock server is nil")
	}

	return mock.MockHandle(
		request,
		ms.stubs,
		ms.invocations,
		ms.random,
		ms.server.telepactSchema,
		ms.enableGeneratedDefaultStub,
		ms.enableOptionalFieldGeneration,
		ms.randomizeOptionalFieldGeneration,
	)
}
