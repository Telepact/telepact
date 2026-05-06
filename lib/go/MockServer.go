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
	"strings"

	"github.com/telepact/telepact/lib/go/internal/mock"
)

// MockServerOptions configures behaviour of the mock server.
type MockServerOptions struct {
	OnError                          func(*TelepactError)
	EnableMessageResponseGeneration  bool
	EnableOptionalFieldGeneration    bool
	RandomizeOptionalFieldGeneration bool
	GeneratedCollectionLengthMin     int
	GeneratedCollectionLengthMax     int
}

// NewMockServerOptions constructs MockServerOptions populated with defaults.
func NewMockServerOptions() *MockServerOptions {
	return &MockServerOptions{
		OnError:                          func(*TelepactError) {},
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
		options.OnError = func(*TelepactError) {}
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

	telepactSchema := NewTelepactSchema(
		mockSchema.Original,
		mockSchema.Full,
		mockSchema.Parsed,
		mockSchema.ParsedRequestHeaders,
		mockSchema.ParsedResponseHeaders,
	)

	functionRouter := NewFunctionRouter(ms.createFunctionRoutes(telepactSchema))
	server, err := NewServer(telepactSchema, functionRouter, serverOptions)
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

func (ms *MockServer) createFunctionRoutes(telepactSchema *TelepactSchema) map[string]FunctionRoute {
	functionRoutes := map[string]FunctionRoute{
		"fn.createStub_": func(_ string, requestMessage Message) (Message, error) {
			argument, err := requestMessage.BodyPayload()
			if err != nil {
				return Message{}, err
			}
			responseHeaders, responseBody, handleErr := mock.HandleCreateStub(argument, &ms.stubs)
			if handleErr != nil {
				return Message{}, NewTelepactError(handleErr.Error())
			}
			return NewMessage(responseHeaders, responseBody), nil
		},
		"fn.verify_": func(_ string, requestMessage Message) (Message, error) {
			argument, err := requestMessage.BodyPayload()
			if err != nil {
				return Message{}, err
			}
			return NewMessage(map[string]any{}, mock.HandleVerify(argument, ms.invocations)), nil
		},
		"fn.verifyNoMoreInteractions_": func(_ string, _ Message) (Message, error) {
			return NewMessage(map[string]any{}, mock.HandleVerifyNoMoreInteractions(ms.invocations)), nil
		},
		"fn.clearCalls_": func(_ string, _ Message) (Message, error) {
			responseHeaders, responseBody, err := mock.HandleClearCalls(&ms.invocations)
			if err != nil {
				return Message{}, NewTelepactError(err.Error())
			}
			return NewMessage(responseHeaders, responseBody), nil
		},
		"fn.clearStubs_": func(_ string, _ Message) (Message, error) {
			responseHeaders, responseBody, err := mock.HandleClearStubs(&ms.stubs)
			if err != nil {
				return Message{}, NewTelepactError(err.Error())
			}
			return NewMessage(responseHeaders, responseBody), nil
		},
		"fn.setRandomSeed_": func(_ string, requestMessage Message) (Message, error) {
			argument, err := requestMessage.BodyPayload()
			if err != nil {
				return Message{}, err
			}
			responseHeaders, responseBody, handleErr := mock.HandleSetRandomSeed(argument, ms.random)
			if handleErr != nil {
				return Message{}, NewTelepactError(handleErr.Error())
			}
			return NewMessage(responseHeaders, responseBody), nil
		},
	}

	for functionName := range telepactSchema.Parsed {
		if !isAutoMockFunctionName(functionName) {
			continue
		}
		functionRoutes[functionName] = ms.createAutoMockRoute(functionName)
	}

	return functionRoutes
}

func (ms *MockServer) createAutoMockRoute(functionName string) FunctionRoute {
	return func(_ string, requestMessage Message) (Message, error) {
		return ms.handleAutoMockFunction(functionName, requestMessage)
	}
}

func (ms *MockServer) handleAutoMockFunction(functionName string, request Message) (Message, error) {
	if ms == nil {
		return Message{}, NewTelepactError("telepact: mock server is nil")
	}

	argument, err := request.BodyPayload()
	if err != nil {
		return Message{}, err
	}

	responseHeaders, responseBody, handleErr := mock.HandleAutoMockFunction(
		request.Headers,
		functionName,
		argument,
		&ms.stubs,
		&ms.invocations,
		ms.random,
		ms.server.telepactSchema.Parsed,
		ms.enableGeneratedDefaultStub,
		ms.enableOptionalFieldGeneration,
		ms.randomizeOptionalFieldGeneration,
	)
	if handleErr != nil {
		return Message{}, NewTelepactError(handleErr.Error())
	}

	return NewMessage(responseHeaders, responseBody), nil
}

func isAutoMockFunctionName(functionName string) bool {
	return len(functionName) > 3 &&
		functionName[:3] == "fn." &&
		!strings.HasSuffix(functionName, ".->") &&
		!strings.HasSuffix(functionName, "_")
}
