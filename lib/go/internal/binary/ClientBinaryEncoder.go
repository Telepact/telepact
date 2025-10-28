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
