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

// ServerBinaryEncoder handles direct binary MessagePack server messages.
type ServerBinaryEncoder struct {
	binaryEncoding *BinaryEncoding
}

// NewServerBinaryEncoder constructs a ServerBinaryEncoder.
func NewServerBinaryEncoder(binaryEncoding *BinaryEncoding) *ServerBinaryEncoder {
	return &ServerBinaryEncoder{binaryEncoding: binaryEncoding}
}

// EncodeToMsgpack encodes a server response directly to MessagePack while translating body keys.
func (e *ServerBinaryEncoder) EncodeToMsgpack(message []any, serializer BinaryMsgpackSerialization) ([]byte, error) {
	if e.binaryEncoding == nil {
		return nil, BinaryEncoderUnavailableError{}
	}
	if len(message) != 2 {
		return nil, fmt.Errorf("invalid message: expected two elements, got %d", len(message))
	}

	headers, err := ensureStringMap(message[0])
	if err != nil {
		return nil, err
	}
	body, err := ensureStringMap(message[1])
	if err != nil {
		return nil, err
	}

	clientKnownRaw, hasClientKnown := headers["@clientKnownBinaryChecksums_"]
	if hasClientKnown {
		delete(headers, "@clientKnownBinaryChecksums_")
	}
	clientKnown, err := extractIntSlice(clientKnownRaw)
	if err != nil {
		return nil, err
	}

	if firstKey(body) != "Ok_" {
		return nil, BinaryEncoderUnavailableError{}
	}

	checksumKnown := false
	for _, checksum := range clientKnown {
		if checksum == e.binaryEncoding.Checksum {
			checksumKnown = true
			break
		}
	}
	if !checksumKnown {
		headers["@enc_"] = e.binaryEncoding.EncodeMap
	}

	headers["@bin_"] = []int{e.binaryEncoding.Checksum}
	return serializer.ToBinaryMsgpack(headers, body, e.binaryEncoding)
}

// DecodeMsgpack decodes a client request directly from MessagePack while translating body keys.
func (e *ServerBinaryEncoder) DecodeMsgpack(data []byte, serializer BinaryMsgpackSerialization) ([]any, error) {
	headers, err := serializer.FromMsgpackHeaders(data)
	if err != nil {
		return nil, err
	}

	clientChecksums, err := extractIntSlice(headers.Headers["@bin_"])
	if err != nil || len(clientChecksums) == 0 {
		return nil, BinaryEncoderUnavailableError{}
	}
	if e.binaryEncoding == nil || clientChecksums[0] != e.binaryEncoding.Checksum {
		return nil, BinaryEncoderUnavailableError{}
	}

	body, err := serializer.FromMsgpackBody(data, headers.BodyOffset, e.binaryEncoding)
	if err != nil {
		return nil, err
	}
	return []any{headers.Headers, body}, nil
}
