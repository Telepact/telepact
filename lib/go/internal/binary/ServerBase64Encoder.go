//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// ServerBase64Encoder implements Base64Encoder for server-side processing.
type ServerBase64Encoder struct{}

// NewServerBase64Encoder constructs a ServerBase64Encoder instance.
func NewServerBase64Encoder() *ServerBase64Encoder {
	return &ServerBase64Encoder{}
}

// Decode is a no-op on the server side; decoding occurs after validation.
func (e *ServerBase64Encoder) Decode(message []any) ([]any, error) {
	return message, nil
}

// Encode applies server-side base64 encoding to the provided message.
func (e *ServerBase64Encoder) Encode(message []any) ([]any, error) {
	if err := ServerBase64Encode(message); err != nil {
		return nil, err
	}
	return message, nil
}
