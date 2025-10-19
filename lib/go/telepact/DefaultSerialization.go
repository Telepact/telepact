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
	"fmt"

	"github.com/vmihailenco/msgpack/v5"
)

// DefaultSerialization implements the Serialization interface using encoding/json and vmihailenco/msgpack.
type DefaultSerialization struct{}

// NewDefaultSerialization constructs a DefaultSerialization instance.
func NewDefaultSerialization() *DefaultSerialization {
	return &DefaultSerialization{}
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
	payload, err := msgpack.Marshal(message)
	if err != nil {
		return nil, NewSerializationError(err, "encode msgpack")
	}
	return payload, nil
}

// FromJSON decodes JSON bytes into a pseudo-JSON object.
func (d *DefaultSerialization) FromJSON(data []byte) (any, error) {
	var out any
	if err := json.Unmarshal(data, &out); err != nil {
		return nil, NewSerializationError(err, "decode JSON")
	}
	return normalizePseudoJSON(out), nil
}

// FromMsgpack decodes MessagePack bytes into a pseudo-JSON object.
func (d *DefaultSerialization) FromMsgpack(data []byte) (any, error) {
	decoder := msgpack.NewDecoder(bytes.NewReader(data))
	decoder.SetMapDecoder(func(dec *msgpack.Decoder) (any, error) {
		length, err := dec.DecodeMapLen()
		if err != nil {
			return nil, err
		}
		result := make(map[any]any, length)
		for i := 0; i < length; i++ {
			key, err := dec.DecodeInterface()
			if err != nil {
				return nil, err
			}
			value, err := dec.DecodeInterface()
			if err != nil {
				return nil, err
			}
			result[key] = value
		}
		return result, nil
	})

	value, err := decoder.DecodeInterface()
	if err != nil {
		return nil, NewSerializationError(err, "decode msgpack")
	}
	return normalizePseudoJSON(value), nil
}

func normalizePseudoJSON(value any) any {
	switch v := value.(type) {
	case map[string]any:
		for key, val := range v {
			v[key] = normalizePseudoJSON(val)
		}
		return v
	case map[any]any:
		result := make(map[string]any, len(v))
		for key, val := range v {
			result[fmt.Sprint(key)] = normalizePseudoJSON(val)
		}
		return result
	case []any:
		for i, val := range v {
			v[i] = normalizePseudoJSON(val)
		}
		return v
	default:
		return v
	}
}
