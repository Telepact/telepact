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

package internal

import "fmt"

type FunctionRouter interface {
	Route(ServerMessage) (ServerMessage, error)
	RequiresAuthentication(functionName string) bool
}

type Middleware func(ServerMessage, FunctionRouter) (ServerMessage, error)

func ProcessBytes(
	requestMessageBytes []byte,
	updateHeaders func(map[string]any),
	deserialize func([]byte) (ServerMessage, error),
	serialize func(ServerMessage) ([]byte, error),
	schema SchemaAccessor,
	onError func(error),
	onRequest func(ServerMessage),
	onResponse func(ServerMessage),
	onAuth func(map[string]any) <-chan map[string]any,
	middleware Middleware,
	functionRouter FunctionRouter,
) (ServerMessage, []byte, error) {
	requestMessage, err := ParseRequestMessage(requestMessageBytes, deserialize, schema, onError)
	if err != nil {
		return ServerMessage{}, nil, err
	}

	safeInvokeMessage(onRequest, requestMessage)

	responseMessage, err := HandleMessage(requestMessage, updateHeaders, schema, middleware, functionRouter, onError, onAuth)
	if err != nil {
		wrapped := wrapUnknownError(err, "telepact server processing failed", "")
		invokeOnError(onError, wrapped)
		return buildUnknownResponse(serialize, wrapped.CaseID())
	}

	safeInvokeMessage(onResponse, responseMessage)

	responseBytes, err := serialize(responseMessage)
	if err != nil {
		wrapped := wrapUnknownError(
			fmt.Errorf("telepact response serialization failed: %w", err),
			"telepact response serialization failed",
			"serialization",
		)
		invokeOnError(onError, wrapped)
		return buildUnknownResponse(serialize, wrapped.CaseID())
	}

	return responseMessage, responseBytes, nil
}

func safeInvokeMessage(callback func(ServerMessage), message ServerMessage) {
	if callback == nil {
		return
	}
	defer func() { _ = recover() }()
	callback(message)
}

func buildUnknownResponse(serialize func(ServerMessage) ([]byte, error), caseID string) (ServerMessage, []byte, error) {
	unknownMessage := newUnknownErrorResponse(map[string]any{}, caseID)

	responseBytes, err := serialize(unknownMessage)
	if err != nil {
		return ServerMessage{}, nil, err
	}

	return unknownMessage, responseBytes, nil
}
