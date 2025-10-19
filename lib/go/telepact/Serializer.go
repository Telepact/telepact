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

// Serializer converts Telepact messages between pseudo-JSON and serialized bytes.
type Serializer struct {
	serializationImpl Serialization
	binaryEncoder     binary.BinaryEncoder
	base64Encoder     binary.Base64Encoder
}

// NewSerializer constructs a Serializer with the provided serialization and encoding strategies.
func NewSerializer(serializationImpl Serialization, binaryEncoder binary.BinaryEncoder, base64Encoder binary.Base64Encoder) *Serializer {
	return &Serializer{
		serializationImpl: serializationImpl,
		binaryEncoder:     binaryEncoder,
		base64Encoder:     base64Encoder,
	}
}

// Serialize converts a Message into its serialized byte representation.
func (s *Serializer) Serialize(message Message) ([]byte, error) {
	return telepactinternal.SerializeInternal(
		message.Headers,
		message.Body,
		s.binaryEncoder,
		s.base64Encoder,
		s.serializationImpl,
		func(err error, context string) error {
			return NewSerializationError(err, context)
		},
	)
}

// Deserialize converts serialized bytes into a Message structure.
func (s *Serializer) Deserialize(messageBytes []byte) (Message, error) {
	headers, body, err := telepactinternal.DeserializeInternal(messageBytes, s.serializationImpl, s.binaryEncoder, s.base64Encoder)
	if err != nil {
		return Message{}, err
	}
	return NewMessage(headers, body), nil
}
