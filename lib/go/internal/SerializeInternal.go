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

package internal

import (
	"errors"
	"fmt"

	"github.com/telepact/telepact/lib/go/internal/binary"
)

// Serialization provides the conversion hooks needed by SerializeInternal and DeserializeInternal.
type Serialization interface {
	ToJSON(message any) ([]byte, error)
	ToMsgpack(message any) ([]byte, error)
	FromJSON(data []byte) (any, error)
	FromMsgpack(data []byte) (any, error)
}

// SerializeInternal converts the provided Telepact headers and body into serialized bytes.
// The wrap function is used to translate intermediate failures into domain-specific errors.
func SerializeInternal(
	headers map[string]any,
	body map[string]any,
	binaryEncoder binary.BinaryEncoder,
	base64Encoder binary.Base64Encoder,
	serializer Serialization,
	wrap func(error, string) error,
) ([]byte, error) {
	if headers == nil || body == nil {
		return nil, wrap(fmt.Errorf("message headers or body is nil"), "serialize message")
	}

	serializeAsBinary := false
	if raw, ok := headers["@binary_"]; ok {
		delete(headers, "@binary_")
		if flag, ok := raw.(bool); ok && flag {
			serializeAsBinary = true
		}
	}

	message := []any{headers, body}

	if serializeAsBinary {
		encoded, err := binaryEncoder.Encode(message)
		if err != nil {
			var unavailableErr binary.BinaryEncoderUnavailableError
			if errors.As(err, &unavailableErr) {
				return serializeAsJSON(message, base64Encoder, serializer, wrap)
			}
			return nil, wrap(err, "encode msgpack")
		}

		payload, err := serializer.ToMsgpack(encoded)
		if err != nil {
			return nil, wrap(err, "encode msgpack")
		}
		return payload, nil
	}

	return serializeAsJSON(message, base64Encoder, serializer, wrap)
}

func serializeAsJSON(
	message []any,
	base64Encoder binary.Base64Encoder,
	serializer Serialization,
	wrap func(error, string) error,
) ([]byte, error) {
	encoded, err := base64Encoder.Encode(message)
	if err != nil {
		return nil, wrap(err, "encode JSON")
	}

	payload, err := serializer.ToJSON(encoded)
	if err != nil {
		return nil, wrap(err, "encode JSON")
	}
	return payload, nil
}
