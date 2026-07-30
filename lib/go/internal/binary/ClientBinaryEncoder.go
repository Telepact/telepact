//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// ClientBinaryEncoder implements BinaryEncoder for Telepact client messages.
type ClientBinaryEncoder struct {
	cache    BinaryEncodingCache
	strategy *ClientBinaryStrategy
}

// NewClientBinaryEncoder constructs a ClientBinaryEncoder with the provided cache.
func NewClientBinaryEncoder(cache BinaryEncodingCache) *ClientBinaryEncoder {
	return &ClientBinaryEncoder{
		cache:    cache,
		strategy: NewClientBinaryStrategy(cache),
	}
}

// Encode encodes a pseudo-JSON client message body into its binary representation.
func (e *ClientBinaryEncoder) Encode(message []any) ([]any, error) {
	return ClientBinaryEncode(message, e.cache, e.strategy)
}

// Decode decodes a binary client message body back into pseudo-JSON.
func (e *ClientBinaryEncoder) Decode(message []any) ([]any, error) {
	return ClientBinaryDecode(message, e.cache, e.strategy)
}
