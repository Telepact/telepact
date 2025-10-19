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
	"context"
	"errors"
	"fmt"

	telepactinternal "github.com/telepact/telepact/lib/go/telepact/internal"
	"github.com/telepact/telepact/lib/go/telepact/internal/binary"
)

// ClientAdapter is the transport-specific function used to exchange Telepact messages.
type ClientAdapter func(ctx context.Context, request Message, serializer *Serializer) (Message, error)

// ClientOptions configure a Client instance.
type ClientOptions struct {
	UseBinary         bool
	AlwaysSendJSON    bool
	TimeoutMSDefault  int
	SerializationImpl Serialization
}

// NewClientOptions returns a ClientOptions struct populated with library defaults.
func NewClientOptions() *ClientOptions {
	return &ClientOptions{
		UseBinary:         false,
		AlwaysSendJSON:    true,
		TimeoutMSDefault:  5000,
		SerializationImpl: NewDefaultSerialization(),
	}
}

// Client coordinates request/response interactions with a Telepact service.
type Client struct {
	adapter          ClientAdapter
	useBinaryDefault bool
	alwaysSendJSON   bool
	timeoutMSDefault int
	serializer       *Serializer
}

// NewClient constructs a Client using the provided adapter and options.
func NewClient(adapter ClientAdapter, options *ClientOptions) (*Client, error) {
	if adapter == nil {
		return nil, errors.New("telepact: client adapter must not be nil")
	}

	if options == nil {
		options = NewClientOptions()
	}

	serializationImpl := options.SerializationImpl
	if serializationImpl == nil {
		serializationImpl = NewDefaultSerialization()
	}

	binaryEncodingCache := binary.NewDefaultBinaryEncodingCache()
	binaryEncoder := binary.NewClientBinaryEncoder(binaryEncodingCache)
	base64Encoder := binary.NewClientBase64Encoder()
	serializer := NewSerializer(serializationImpl, binaryEncoder, base64Encoder)

	return &Client{
		adapter:          adapter,
		useBinaryDefault: options.UseBinary,
		alwaysSendJSON:   options.AlwaysSendJSON,
		timeoutMSDefault: options.TimeoutMSDefault,
		serializer:       serializer,
	}, nil
}

// RequestWithContext executes the adapter using the supplied context, applying Telepact defaults.
func (c *Client) RequestWithContext(ctx context.Context, request Message) (Message, error) {
	if c == nil {
		return Message{}, NewTelepactError("telepact: client is nil")
	}

	if ctx == nil {
		ctx = context.Background()
	}

	internalRequest := telepactinternal.NewClientMessage(request.Headers, request.Body)

	adapter := func(ctx context.Context, msg *telepactinternal.ClientMessage) (*telepactinternal.ClientMessage, error) {
		resp, err := c.adapter(ctx, Message{Headers: msg.Headers, Body: msg.Body}, c.serializer)
		if err != nil {
			return nil, err
		}
		return telepactinternal.NewClientMessage(resp.Headers, resp.Body), nil
	}

	internalResponse, err := telepactinternal.ClientHandleMessage(
		ctx,
		internalRequest,
		adapter,
		c.timeoutMSDefault,
		c.useBinaryDefault,
		c.alwaysSendJSON,
	)
	if err != nil {
		return Message{}, NewTelepactError(fmt.Sprintf("client request failed: %v", err))
	}

	return Message{Headers: internalResponse.Headers, Body: internalResponse.Body}, nil
}

// Request executes the adapter using a background context.
func (c *Client) Request(request Message) (Message, error) {
	return c.RequestWithContext(context.Background(), request)
}

// Serializer returns the serializer associated with the client.
func (c *Client) Serializer() *Serializer {
	if c == nil {
		return nil
	}
	return c.serializer
}
