//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// ServerBinaryEncoder adapts ServerBinaryEncode and ServerBinaryDecode to the BinaryEncoder interface.
type ServerBinaryEncoder struct {
	binaryEncoding *BinaryEncoding
}

// NewServerBinaryEncoder constructs a ServerBinaryEncoder.
func NewServerBinaryEncoder(binaryEncoding *BinaryEncoding) *ServerBinaryEncoder {
	return &ServerBinaryEncoder{binaryEncoding: binaryEncoding}
}

// Encode encodes the provided message using the underlying binary encoding.
func (e *ServerBinaryEncoder) Encode(message []any) ([]any, error) {
	return ServerBinaryEncode(message, e.binaryEncoding)
}

// Decode decodes the provided message using the underlying binary encoding.
func (e *ServerBinaryEncoder) Decode(message []any) ([]any, error) {
	return ServerBinaryDecode(message, e.binaryEncoding)
}
