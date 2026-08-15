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
	"bytes"
	"encoding/json"

	telepactbinary "github.com/telepact/telepact/lib/go/internal/binary"
)

// DefaultSerialization implements the Serialization interface using encoding/json and MessagePack.
type DefaultSerialization struct {
	binaryMsgpack *telepactbinary.BinaryMsgpackCodec
}

// NewDefaultSerialization constructs a DefaultSerialization instance.
func NewDefaultSerialization() *DefaultSerialization {
	return &DefaultSerialization{binaryMsgpack: telepactbinary.NewBinaryMsgpackCodec()}
}

// ToJSON converts a pseudo-JSON object into its JSON-encoded bytes representation.
func (d *DefaultSerialization) ToJSON(message any) ([]byte, error) {
	payload, err := json.Marshal(message)
	if err != nil {
		return nil, NewSerializationError(err, "encode JSON")
	}
	return payload, nil
}

// ToMsgpack converts a pseudo-JSON object into its MessagePack-encoded bytes representation.
func (d *DefaultSerialization) ToMsgpack(message any) ([]byte, error) {
	payload, err := d.binaryMsgpack.ToMsgpack(message)
	if err != nil {
		return nil, NewSerializationError(err, "encode msgpack")
	}
	return payload, nil
}

// FromJSON decodes JSON bytes into a pseudo-JSON object.
func (d *DefaultSerialization) FromJSON(data []byte) (any, error) {
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.UseNumber()

	var out any
	if err := decoder.Decode(&out); err != nil {
		return nil, NewSerializationError(err, "decode JSON")
	}
	return telepactbinary.NormalizePseudoJSON(out), nil
}

// FromMsgpack decodes MessagePack bytes into a pseudo-JSON object.
func (d *DefaultSerialization) FromMsgpack(data []byte) (any, error) {
	value, err := d.binaryMsgpack.FromMsgpack(data)
	if err != nil {
		return nil, NewSerializationError(err, "decode msgpack")
	}
	return value, nil
}

// ToBinaryMsgpack packs a binary Telepact message while translating body keys in the same walk.
func (d *DefaultSerialization) ToBinaryMsgpack(headers map[string]any, body map[string]any, encoding *telepactbinary.BinaryEncoding) ([]byte, error) {
	payload, err := d.binaryMsgpack.ToBinaryMsgpack(headers, body, encoding)
	if err != nil {
		return nil, NewSerializationError(err, "encode binary msgpack")
	}
	return payload, nil
}

// FromMsgpackHeaders decodes the top-level headers and reports where the body starts.
func (d *DefaultSerialization) FromMsgpackHeaders(data []byte) (telepactbinary.MsgpackHeaders, error) {
	headers, err := d.binaryMsgpack.FromMsgpackHeaders(data)
	if err != nil {
		return telepactbinary.MsgpackHeaders{}, NewSerializationError(err, "decode msgpack headers")
	}
	return headers, nil
}

// FromMsgpackBody decodes the body while translating binary map keys.
func (d *DefaultSerialization) FromMsgpackBody(data []byte, offset int, encoding *telepactbinary.BinaryEncoding) (map[string]any, error) {
	body, err := d.binaryMsgpack.FromMsgpackBody(data, offset, encoding)
	if err != nil {
		return nil, NewSerializationError(err, "decode binary msgpack body")
	}
	return body, nil
}
