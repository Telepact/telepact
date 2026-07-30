//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// ClientBase64Encoder implements the Base64Encoder interface for Telepact client messages.
type ClientBase64Encoder struct{}

// NewClientBase64Encoder constructs a new ClientBase64Encoder instance.
func NewClientBase64Encoder() *ClientBase64Encoder {
	return &ClientBase64Encoder{}
}

// Decode decodes base64-encoded payload fields specified by the pseudo-JSON headers.
func (e *ClientBase64Encoder) Decode(message []any) ([]any, error) {
	if err := ClientBase64Decode(message); err != nil {
		return nil, err
	}
	return message, nil
}

// Encode traverses the message body and encodes any raw byte slices into base64 strings.
func (e *ClientBase64Encoder) Encode(message []any) ([]any, error) {
	if err := ClientBase64Encode(message); err != nil {
		return nil, err
	}
	return message, nil
}
