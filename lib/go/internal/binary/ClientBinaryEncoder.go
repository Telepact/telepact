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

import "fmt"

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

// EncodeToMsgpack encodes a client request directly to MessagePack while translating body keys.
func (e *ClientBinaryEncoder) EncodeToMsgpack(message []any, serializer BinaryMsgpackSerialization) ([]byte, error) {
	if len(message) < 2 {
		return nil, fmt.Errorf("invalid message: expected headers and body, got %d elements", len(message))
	}

	headers, err := ensureStringMap(message[0])
	if err != nil {
		return nil, err
	}
	body, err := ensureStringMap(message[1])
	if err != nil {
		return nil, err
	}

	forceSendJSON := isStrictTrue(headers["_forceSendJson"])
	delete(headers, "_forceSendJson")

	checksums := e.strategy.GetCurrentChecksums()
	headers["@bin_"] = checksums

	if forceSendJSON || len(checksums) > 1 || len(checksums) == 0 {
		return nil, BinaryEncoderUnavailableError{}
	}

	encoding := e.cache.Get(checksums[0])
	if encoding == nil {
		return nil, BinaryEncoderUnavailableError{}
	}

	return serializer.ToBinaryMsgpack(headers, body, encoding)
}

// DecodeMsgpack decodes a server response directly from MessagePack while translating body keys.
func (e *ClientBinaryEncoder) DecodeMsgpack(data []byte, serializer BinaryMsgpackSerialization) ([]any, error) {
	headers, err := serializer.FromMsgpackHeaders(data)
	if err != nil {
		return nil, err
	}

	checksums, err := extractIntSlice(headers.Headers["@bin_"])
	if err != nil || len(checksums) == 0 {
		return nil, BinaryEncoderUnavailableError{}
	}
	binaryChecksum := checksums[0]

	if encodingRaw, ok := headers.Headers["@enc_"]; ok {
		encodingMap, castErr := toStringIntMap(encodingRaw)
		if castErr != nil {
			return nil, castErr
		}
		e.cache.Add(binaryChecksum, encodingMap)
	}

	e.strategy.UpdateChecksum(binaryChecksum)
	currentChecksums := e.strategy.GetCurrentChecksums()
	if len(currentChecksums) == 0 {
		return nil, BinaryEncoderUnavailableError{}
	}

	encoding := e.cache.Get(currentChecksums[0])
	if encoding == nil {
		return nil, BinaryEncoderUnavailableError{}
	}

	body, err := serializer.FromMsgpackBody(data, headers.BodyOffset, encoding)
	if err != nil {
		return nil, err
	}
	return []any{headers.Headers, body}, nil
}
