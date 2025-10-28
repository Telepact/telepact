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

func ProcessBytes(
	requestMessageBytes []byte,
	overrideHeaders map[string]any,
	deserialize func([]byte) (ServerMessage, error),
	serialize func(ServerMessage) ([]byte, error),
	schema SchemaAccessor,
	onError func(error),
	onRequest func(ServerMessage),
	onResponse func(ServerMessage),
	handler func(ServerMessage) (ServerMessage, error),
) (ServerMessage, []byte, error) {
	requestMessage, err := ParseRequestMessage(requestMessageBytes, deserialize, schema, onError)
	if err != nil {
		return ServerMessage{}, nil, err
	}

	safeInvokeMessage(onRequest, requestMessage)

	responseMessage, err := HandleMessage(requestMessage, overrideHeaders, schema, handler, onError)
	if err != nil {
		invokeOnError(onError, err)
		return buildUnknownResponse(serialize)
	}

	safeInvokeMessage(onResponse, responseMessage)

	responseBytes, err := serialize(responseMessage)
	if err != nil {
		invokeOnError(onError, err)
		return buildUnknownResponse(serialize)
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

func buildUnknownResponse(serialize func(ServerMessage) ([]byte, error)) (ServerMessage, []byte, error) {
	unknownMessage := ServerMessage{
		Headers: map[string]any{},
		Body:    map[string]any{"ErrorUnknown_": map[string]any{}},
	}

	responseBytes, err := serialize(unknownMessage)
	if err != nil {
		return ServerMessage{}, nil, err
	}

	return unknownMessage, responseBytes, nil
}
