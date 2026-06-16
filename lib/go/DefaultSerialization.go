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
	"math"
	"reflect"
	"strconv"
	"strings"

	telepactbinary "github.com/telepact/telepact/lib/go/internal/binary"
	"github.com/vmihailenco/msgpack/v5"
	"github.com/vmihailenco/msgpack/v5/msgpcode"
)

const msgpackJSONNumberExtType = 0x2a

type msgpackJSONNumber struct {
	Value string
}

func (n *msgpackJSONNumber) MarshalMsgpack() ([]byte, error) {
	return []byte(n.Value), nil
}

func (n *msgpackJSONNumber) UnmarshalMsgpack(data []byte) error {
	n.Value = string(data)
	return nil
}

func init() {
	msgpack.RegisterExt(msgpackJSONNumberExtType, (*msgpackJSONNumber)(nil))
}

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
	prepared := wrapJSONNumbers(message)
	payload, err := msgpack.Marshal(prepared)
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
	return normalizePseudoJSON(unwrapJSONNumbers(value)), nil
}

// ToBinaryMsgpack packs a binary Telepact message while translating body keys in the same walk.
func (d *DefaultSerialization) ToBinaryMsgpack(headers map[string]any, body map[string]any, encoding *telepactbinary.BinaryEncoding) ([]byte, error) {
	var buffer bytes.Buffer
	encoder := msgpack.NewEncoder(&buffer)
	if err := encoder.EncodeArrayLen(2); err != nil {
		return nil, NewSerializationError(err, "encode binary msgpack")
	}
	if err := packMsgpackValue(encoder, headers, nil); err != nil {
		return nil, NewSerializationError(err, "encode binary msgpack")
	}
	if err := packMsgpackValue(encoder, body, encoding); err != nil {
		return nil, NewSerializationError(err, "encode binary msgpack")
	}
	return buffer.Bytes(), nil
}

// FromMsgpackHeaders decodes the top-level headers and reports where the body starts.
func (d *DefaultSerialization) FromMsgpackHeaders(data []byte) (telepactbinary.MsgpackHeaders, error) {
	reader := bytes.NewReader(data)
	decoder := msgpack.NewDecoder(reader)
	length, err := decoder.DecodeArrayLen()
	if err != nil {
		return telepactbinary.MsgpackHeaders{}, NewSerializationError(err, "decode msgpack headers")
	}
	if length != 2 {
		return telepactbinary.MsgpackHeaders{}, NewSerializationError(fmt.Errorf("expected Telepact msgpack message array"), "decode msgpack headers")
	}
	value, err := unpackMsgpackValue(decoder)
	if err != nil {
		return telepactbinary.MsgpackHeaders{}, NewSerializationError(err, "decode msgpack headers")
	}
	headers, ok := value.(map[string]any)
	if !ok {
		return telepactbinary.MsgpackHeaders{}, NewSerializationError(fmt.Errorf("expected msgpack headers map"), "decode msgpack headers")
	}
	return telepactbinary.MsgpackHeaders{
		Headers:    headers,
		BodyOffset: int(reader.Size() - int64(reader.Len())),
	}, nil
}

// FromMsgpackBody decodes the body while translating binary map keys.
func (d *DefaultSerialization) FromMsgpackBody(data []byte, offset int, encoding *telepactbinary.BinaryEncoding) (map[string]any, error) {
	decoder := msgpack.NewDecoder(bytes.NewReader(data[offset:]))
	value, err := unpackBinaryMsgpackValue(decoder, encoding)
	if err != nil {
		return nil, NewSerializationError(err, "decode binary msgpack body")
	}
	body, ok := value.(map[string]any)
	if !ok {
		return nil, NewSerializationError(fmt.Errorf("expected msgpack body map"), "decode binary msgpack body")
	}
	return body, nil
}

func packMsgpackValue(encoder *msgpack.Encoder, value any, encoding *telepactbinary.BinaryEncoding) error {
	switch typed := value.(type) {
	case nil:
		return encoder.EncodeNil()
	case map[string]any:
		if err := encoder.EncodeMapLen(len(typed)); err != nil {
			return err
		}
		for key, val := range typed {
			if encoding != nil {
				if encoded, ok := encoding.EncodeMap[key]; ok {
					if err := encoder.EncodeInt(int64(encoded)); err != nil {
						return err
					}
				} else if err := encoder.EncodeString(key); err != nil {
					return err
				}
			} else if err := encoder.EncodeString(key); err != nil {
				return err
			}
			if err := packMsgpackValue(encoder, val, encoding); err != nil {
				return err
			}
		}
		return nil
	case map[any]any:
		if err := encoder.EncodeMapLen(len(typed)); err != nil {
			return err
		}
		for key, val := range typed {
			if keyString, ok := key.(string); ok && encoding != nil {
				if encoded, present := encoding.EncodeMap[keyString]; present {
					if err := encoder.EncodeInt(int64(encoded)); err != nil {
						return err
					}
				} else if err := packMsgpackValue(encoder, key, nil); err != nil {
					return err
				}
			} else if err := packMsgpackValue(encoder, key, nil); err != nil {
				return err
			}
			if err := packMsgpackValue(encoder, val, encoding); err != nil {
				return err
			}
		}
		return nil
	case []any:
		if ok, err := packUniformMapArray(encoder, typed, encoding); ok || err != nil {
			return err
		}
		if err := encoder.EncodeArrayLen(len(typed)); err != nil {
			return err
		}
		for _, val := range typed {
			if err := packMsgpackValue(encoder, val, encoding); err != nil {
				return err
			}
		}
		return nil
	case json.Number:
		return encoder.Encode(wrapJSONNumbers(typed))
	default:
		return encoder.Encode(value)
	}
}

func packUniformMapArray(encoder *msgpack.Encoder, list []any, encoding *telepactbinary.BinaryEncoding) (bool, error) {
	if encoding == nil || len(list) < 16 {
		return false, nil
	}
	first, ok := list[0].(map[string]any)
	if !ok || len(first) == 0 {
		return false, nil
	}

	rawKeys := make([]string, 0, len(first))
	encodedKeys := make([]int, 0, len(first))
	for key := range first {
		encoded, present := encoding.EncodeMap[key]
		if !present {
			return false, nil
		}
		rawKeys = append(rawKeys, key)
		encodedKeys = append(encodedKeys, encoded)
	}

	if err := encoder.EncodeArrayLen(len(list)); err != nil {
		return true, err
	}
	for _, item := range list {
		row := item.(map[string]any)
		if err := encoder.EncodeMapLen(len(rawKeys)); err != nil {
			return true, err
		}
		for index, key := range rawKeys {
			if err := encoder.EncodeInt(int64(encodedKeys[index])); err != nil {
				return true, err
			}
			if err := packMsgpackValue(encoder, row[key], encoding); err != nil {
				return true, err
			}
		}
	}
	return true, nil
}

func unpackBinaryMsgpackValue(decoder *msgpack.Decoder, encoding *telepactbinary.BinaryEncoding) (any, error) {
	code, err := decoder.PeekCode()
	if err != nil {
		return nil, err
	}
	if isMsgpackArrayCode(code) {
		length, err := decoder.DecodeArrayLen()
		if err != nil {
			return nil, err
		}
		result := make([]any, length)
		if length >= 16 {
			nextCode, err := decoder.PeekCode()
			if err != nil {
				return nil, err
			}
			if isMsgpackMapCode(nextCode) {
				first, rawKeys, decodedKeys, err := unpackBinaryMsgpackMap(decoder, encoding, nil, nil)
				if err != nil {
					return nil, err
				}
				result[0] = first
				for index := 1; index < length; index++ {
					nextCode, err := decoder.PeekCode()
					if err != nil {
						return nil, err
					}
					if isMsgpackMapCode(nextCode) {
						value, _, _, err := unpackBinaryMsgpackMap(decoder, encoding, rawKeys, decodedKeys)
						if err != nil {
							return nil, err
						}
						result[index] = value
					} else {
						value, err := unpackBinaryMsgpackValue(decoder, encoding)
						if err != nil {
							return nil, err
						}
						result[index] = value
					}
				}
				return result, nil
			}
		}
		for index := 0; index < length; index++ {
			value, err := unpackBinaryMsgpackValue(decoder, encoding)
			if err != nil {
				return nil, err
			}
			result[index] = value
		}
		return result, nil
	}
	if isMsgpackMapCode(code) {
		result, _, _, err := unpackBinaryMsgpackMap(decoder, encoding, nil, nil)
		return result, err
	}
	return unpackMsgpackValue(decoder)
}

func unpackBinaryMsgpackMap(decoder *msgpack.Decoder, encoding *telepactbinary.BinaryEncoding, expectedRawKeys []any, expectedDecodedKeys []string) (map[string]any, []any, []string, error) {
	length, err := decoder.DecodeMapLen()
	if err != nil {
		return nil, nil, nil, err
	}
	result := make(map[string]any, length)
	collectKeys := expectedRawKeys == nil || expectedDecodedKeys == nil
	rawKeys := expectedRawKeys
	decodedKeys := expectedDecodedKeys
	if collectKeys {
		rawKeys = make([]any, 0, length)
		decodedKeys = make([]string, 0, length)
	}
	canReuseKeys := !collectKeys && len(expectedRawKeys) == length

	for index := 0; index < length; index++ {
		key, err := unpackMsgpackValue(decoder)
		if err != nil {
			return nil, nil, nil, err
		}
		value, err := unpackBinaryMsgpackValue(decoder, encoding)
		if err != nil {
			return nil, nil, nil, err
		}

		var decodedKey string
		if canReuseKeys && reflect.DeepEqual(key, expectedRawKeys[index]) {
			decodedKey = expectedDecodedKeys[index]
		} else {
			decodedKey, err = decodeBinaryMsgpackKey(key, encoding)
			if err != nil {
				return nil, nil, nil, err
			}
		}
		if collectKeys {
			rawKeys = append(rawKeys, key)
			decodedKeys = append(decodedKeys, decodedKey)
		}
		result[decodedKey] = value
	}
	return result, rawKeys, decodedKeys, nil
}

func unpackMsgpackValue(decoder *msgpack.Decoder) (any, error) {
	code, err := decoder.PeekCode()
	if err != nil {
		return nil, err
	}
	if isMsgpackArrayCode(code) {
		length, err := decoder.DecodeArrayLen()
		if err != nil {
			return nil, err
		}
		result := make([]any, length)
		for index := 0; index < length; index++ {
			value, err := unpackMsgpackValue(decoder)
			if err != nil {
				return nil, err
			}
			result[index] = value
		}
		return result, nil
	}
	if isMsgpackMapCode(code) {
		length, err := decoder.DecodeMapLen()
		if err != nil {
			return nil, err
		}
		result := make(map[string]any, length)
		for index := 0; index < length; index++ {
			key, err := unpackMsgpackValue(decoder)
			if err != nil {
				return nil, err
			}
			value, err := unpackMsgpackValue(decoder)
			if err != nil {
				return nil, err
			}
			result[fmt.Sprint(key)] = value
		}
		return result, nil
	}
	value, err := decoder.DecodeInterface()
	if err != nil {
		return nil, err
	}
	return normalizePseudoJSON(unwrapJSONNumbers(value)), nil
}

func isMsgpackArrayCode(code byte) bool {
	return msgpcode.IsFixedArray(code) || code == msgpcode.Array16 || code == msgpcode.Array32
}

func isMsgpackMapCode(code byte) bool {
	return msgpcode.IsFixedMap(code) || code == msgpcode.Map16 || code == msgpcode.Map32
}

func decodeBinaryMsgpackKey(key any, encoding *telepactbinary.BinaryEncoding) (string, error) {
	if keyString, ok := key.(string); ok {
		return keyString, nil
	}
	if intKey, ok := msgpackKeyToInt(key); ok && encoding != nil && intKey >= 0 && intKey < len(encoding.DecodeTable) {
		decoded := encoding.DecodeTable[intKey]
		if decoded != "" {
			return decoded, nil
		}
	}
	return "", telepactbinary.NewBinaryEncodingMissing(key)
}

func msgpackKeyToInt(value any) (int, bool) {
	switch typed := value.(type) {
	case int:
		return typed, true
	case int8:
		return int(typed), true
	case int16:
		return int(typed), true
	case int32:
		return int(typed), true
	case int64:
		return int(typed), true
	case uint:
		return int(typed), true
	case uint8:
		return int(typed), true
	case uint16:
		return int(typed), true
	case uint32:
		return int(typed), true
	case uint64:
		return int(typed), true
	default:
		return 0, false
	}
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
	case float64:
		if math.Trunc(v) == v && v <= math.MaxInt64 && v >= math.MinInt64 {
			return int64(v)
		}
		return v
	case json.Number:
		normalized, ok := normalizeJSONNumber(v)
		if ok {
			return normalized
		}
		return v
	default:
		return v
	}
}

func wrapJSONNumbers(value any) any {
	switch v := value.(type) {
	case map[string]any:
		result := make(map[string]any, len(v))
		for key, val := range v {
			result[key] = wrapJSONNumbers(val)
		}
		return result
	case map[any]any:
		result := make(map[any]any, len(v))
		for key, val := range v {
			result[key] = wrapJSONNumbers(val)
		}
		return result
	case []any:
		result := make([]any, len(v))
		for i, val := range v {
			result[i] = wrapJSONNumbers(val)
		}
		return result
	case json.Number:
		return &msgpackJSONNumber{Value: string(v)}
	case *msgpackJSONNumber:
		return v
	default:
		return value
	}
}

func unwrapJSONNumbers(value any) any {
	switch v := value.(type) {
	case map[string]any:
		for key, val := range v {
			v[key] = unwrapJSONNumbers(val)
		}
		return v
	case map[any]any:
		for key, val := range v {
			v[key] = unwrapJSONNumbers(val)
		}
		return v
	case []any:
		for i, val := range v {
			v[i] = unwrapJSONNumbers(val)
		}
		return v
	case *msgpackJSONNumber:
		if v == nil {
			return nil
		}
		return json.Number(v.Value)
	case msgpackJSONNumber:
		return json.Number(v.Value)
	default:
		return value
	}
}

func normalizeJSONNumber(value json.Number) (any, bool) {
	raw := string(value)

	if !strings.ContainsAny(raw, ".eE") {
		if i, err := strconv.ParseInt(raw, 10, 64); err == nil {
			return i, true
		}
		return nil, false
	}

	if f, err := strconv.ParseFloat(raw, 64); err == nil && !math.IsNaN(f) && !math.IsInf(f, 0) {
		return f, true
	}

	return nil, false
}
