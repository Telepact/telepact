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
	telepactinternal "github.com/telepact/telepact/lib/go/internal"
	"github.com/telepact/telepact/lib/go/internal/binary"
)

// ServerOptions configures server behaviour.
type ServerOptions struct {
	Middleware    ServerMiddleware
	OnError       func(error)
	OnRequest     func(Message)
	OnResponse    func(Message)
	OnAuth        func(map[string]any) map[string]any
	AuthRequired  bool
	Serialization Serialization
}

// NewServerOptions constructs ServerOptions populated with defaults.
func NewServerOptions() *ServerOptions {
	return &ServerOptions{
		Middleware: func(requestMessage Message, functionRouter *FunctionRouter) (Message, error) {
			return functionRouter.Route(requestMessage)
		},
		OnError:       func(error) {},
		OnRequest:     func(Message) {},
		OnResponse:    func(Message) {},
		OnAuth:        func(map[string]any) map[string]any { return map[string]any{} },
		AuthRequired:  true,
		Serialization: NewDefaultSerialization(),
	}
}

// Server represents a Telepact server instance.
type Server struct {
	functionRouter *FunctionRouter
	middleware     ServerMiddleware
	onError        func(error)
	onRequest      func(Message)
	onResponse     func(Message)
	onAuth         func(map[string]any) map[string]any
	telepactSchema *TelepactSchema
	serializer     *Serializer
}

// NewServer constructs a Server using the supplied schema and options.
func NewServer(telepactSchema *TelepactSchema, functionRouter *FunctionRouter, options *ServerOptions) (*Server, error) {
	if telepactSchema == nil {
		return nil, NewTelepactError("telepact: schema must not be nil")
	}
	if functionRouter == nil {
		functionRouter = NewFunctionRouter()
	}

	if options == nil {
		options = NewServerOptions()
	}

	if options.Middleware == nil {
		options.Middleware = func(requestMessage Message, functionRouter *FunctionRouter) (Message, error) {
			return functionRouter.Route(requestMessage)
		}
	}
	if options.OnError == nil {
		options.OnError = func(error) {}
	}
	if options.OnRequest == nil {
		options.OnRequest = func(Message) {}
	}
	if options.OnResponse == nil {
		options.OnResponse = func(Message) {}
	}
	if options.OnAuth == nil {
		options.OnAuth = func(map[string]any) map[string]any { return map[string]any{} }
	}

	serializationImpl := options.Serialization
	if serializationImpl == nil {
		serializationImpl = NewDefaultSerialization()
	}

	binaryEncoding, err := binary.ConstructBinaryEncoding(telepactSchema.Parsed)
	if err != nil {
		return nil, err
	}

	binaryEncoder := binary.NewServerBinaryEncoder(binaryEncoding)
	base64Encoder := binary.NewServerBase64Encoder()
	serializer := NewSerializer(serializationImpl, binaryEncoder, base64Encoder)

	if _, exists := telepactSchema.Parsed["union.Auth_"]; !exists && options.AuthRequired {
		return nil, NewTelepactError("Unauthenticated server. Either define a `union.Auth_` in your schema or set `options.auth_required` to `false`.")
	}

	return &Server{
		functionRouter: functionRouter,
		middleware:     options.Middleware,
		onError:        options.OnError,
		onRequest:      options.OnRequest,
		onResponse:     options.OnResponse,
		onAuth:         options.OnAuth,
		telepactSchema: telepactSchema,
		serializer:     serializer,
	}, nil
}

// ProcessWithHeaders processes a request message with optional override headers.
func (s *Server) ProcessWithHeaders(requestMessageBytes []byte, overrideHeaders map[string]any) (Response, error) {
	if s == nil {
		return Response{}, NewTelepactError("telepact: server is nil")
	}

	if overrideHeaders == nil {
		overrideHeaders = map[string]any{}
	}

	deserialize := func(bytes []byte) (telepactinternal.ServerMessage, error) {
		msg, err := s.serializer.Deserialize(bytes)
		if err != nil {
			return telepactinternal.ServerMessage{}, err
		}
		return telepactinternal.ServerMessage{Headers: msg.Headers, Body: msg.Body}, nil
	}

	serialize := func(message telepactinternal.ServerMessage) ([]byte, error) {
		goMessage := NewMessage(message.Headers, message.Body)
		return s.serializer.Serialize(goMessage)
	}

	internalOnRequest := func(message telepactinternal.ServerMessage) {
		s.onRequest(NewMessage(message.Headers, message.Body))
	}

	internalOnResponse := func(message telepactinternal.ServerMessage) {
		s.onResponse(NewMessage(message.Headers, message.Body))
	}

	internalMiddleware := func(
		requestMessage telepactinternal.ServerMessage,
	) (telepactinternal.ServerMessage, error) {
		response, err := s.middleware(NewMessage(requestMessage.Headers, requestMessage.Body), s.functionRouter)
		if err != nil {
			return telepactinternal.ServerMessage{}, err
		}
		return telepactinternal.ServerMessage{Headers: response.Headers, Body: response.Body}, nil
	}

	responseMessage, responseBytes, err := telepactinternal.ProcessBytes(
		requestMessageBytes,
		overrideHeaders,
		deserialize,
		serialize,
		s.telepactSchema,
		s.onError,
		internalOnRequest,
		internalOnResponse,
		s.onAuth,
		internalMiddleware,
	)
	if err != nil {
		return Response{}, err
	}

	return NewResponse(responseBytes, responseMessage.Headers), nil
}

// Process processes a request message without any header overrides.
func (s *Server) Process(requestMessageBytes []byte) (Response, error) {
	return s.ProcessWithHeaders(requestMessageBytes, nil)
}

// TelepactSchema returns the schema associated with the server.
func (s *Server) TelepactSchema() *TelepactSchema {
	if s == nil {
		return nil
	}
	return s.telepactSchema
}

// Serializer returns the serializer associated with the server.
func (s *Server) Serializer() *Serializer {
	if s == nil {
		return nil
	}
	return s.serializer
}
