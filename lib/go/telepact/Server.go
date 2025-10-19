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
	telepactinternal "github.com/telepact/telepact/lib/go/telepact/internal"
	"github.com/telepact/telepact/lib/go/telepact/internal/binary"
)

// ServerHandler processes incoming Telepact messages and returns a response message.
type ServerHandler func(Message) (Message, error)

// ServerOptions configures server behaviour.
type ServerOptions struct {
	OnError       func(error)
	OnRequest     func(Message)
	OnResponse    func(Message)
	AuthRequired  bool
	Serialization Serialization
}

// NewServerOptions constructs ServerOptions populated with defaults.
func NewServerOptions() *ServerOptions {
	return &ServerOptions{
		OnError:       func(error) {},
		OnRequest:     func(Message) {},
		OnResponse:    func(Message) {},
		AuthRequired:  true,
		Serialization: NewDefaultSerialization(),
	}
}

// Server represents a Telepact server instance.
type Server struct {
	handler        ServerHandler
	onError        func(error)
	onRequest      func(Message)
	onResponse     func(Message)
	telepactSchema *TelepactSchema
	serializer     *Serializer
}

// NewServer constructs a Server using the supplied schema, handler, and options.
func NewServer(telepactSchema *TelepactSchema, handler ServerHandler, options *ServerOptions) (*Server, error) {
	if telepactSchema == nil {
		return nil, NewTelepactError("telepact: schema must not be nil")
	}
	if handler == nil {
		return nil, NewTelepactError("telepact: handler must not be nil")
	}

	if options == nil {
		options = NewServerOptions()
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

	serializationImpl := options.Serialization
	if serializationImpl == nil {
		serializationImpl = NewDefaultSerialization()
	}

	binaryEncoding, err := binary.ConstructBinaryEncoding(telepactSchema)
	if err != nil {
		return nil, err
	}

	binaryEncoder := binary.NewServerBinaryEncoder(binaryEncoding)
	base64Encoder := binary.NewServerBase64Encoder()
	serializer := NewSerializer(serializationImpl, binaryEncoder, base64Encoder)

	if _, exists := telepactSchema.Parsed["struct.Auth_"]; !exists && options.AuthRequired {
		return nil, NewTelepactError("Unauthenticated server. Either define a `struct.Auth_` in your schema or set `options.auth_required` to `false`.")
	}

	return &Server{
		handler:        handler,
		onError:        options.OnError,
		onRequest:      options.OnRequest,
		onResponse:     options.OnResponse,
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

	return telepactinternal.ProcessBytes(
		requestMessageBytes,
		overrideHeaders,
		s.serializer,
		s.telepactSchema,
		s.onError,
		s.onRequest,
		s.onResponse,
		s.handler,
	)
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
