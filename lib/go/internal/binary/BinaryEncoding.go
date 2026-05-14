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

// BinaryEncoding stores lookup tables for translating between string keys and integer codes
// in the binary encoding representation.
type BinaryEncoding struct {
	EncodeMap                map[string]int
	DecodeMap                map[int]string
	Checksum                 int
	Keys                     []string
	RequestPlanDescriptors   []any
	ResponsePlanDescriptors  []any
}

// NewBinaryEncoding constructs a BinaryEncoding from the provided encoding map and checksum.
func NewBinaryEncoding(binaryEncodingMap map[string]int, checksum int, keys []string, requestPlanDescriptors []any, responsePlanDescriptors []any) *BinaryEncoding {
	encodeMap := make(map[string]int, len(binaryEncodingMap))
	for key, value := range binaryEncodingMap {
		encodeMap[key] = value
	}

	decodeMap := make(map[int]string, len(binaryEncodingMap))
	for key, value := range encodeMap {
		decodeMap[value] = key
	}

	return &BinaryEncoding{
		EncodeMap:               encodeMap,
		DecodeMap:               decodeMap,
		Checksum:                checksum,
		Keys:                    append([]string{}, keys...),
		RequestPlanDescriptors:  append([]any{}, requestPlanDescriptors...),
		ResponsePlanDescriptors: append([]any{}, responsePlanDescriptors...),
	}
}

func (b *BinaryEncoding) NegotiationDescriptor(functionID *int, includeBundle bool) map[string]any {
	descriptor := map[string]any{
		"v": 1,
	}
	if functionID != nil {
		descriptor["p"] = *functionID
	}
	if includeBundle {
		descriptor["k"] = append([]string{}, b.Keys...)
		descriptor["q"] = append([]any{}, b.RequestPlanDescriptors...)
		descriptor["s"] = append([]any{}, b.ResponsePlanDescriptors...)
	}
	return descriptor
}

func BinaryEncodingFromNegotiationDescriptor(checksum int, descriptor map[string]any) (*BinaryEncoding, error) {
	rawKeys, ok := descriptor["k"].([]any)
	if !ok {
		return nil, fmt.Errorf("invalid binary negotiation keys")
	}

	keys := make([]string, 0, len(rawKeys))
	encodingMap := make(map[string]int, len(rawKeys))
	for index, rawKey := range rawKeys {
		key, ok := rawKey.(string)
		if !ok {
			return nil, fmt.Errorf("invalid binary negotiation key %v", rawKey)
		}
		keys = append(keys, key)
		encodingMap[key] = index
	}

	requestPlanDescriptors, _ := descriptor["q"].([]any)
	responsePlanDescriptors, _ := descriptor["s"].([]any)
	return NewBinaryEncoding(encodingMap, checksum, keys, requestPlanDescriptors, responsePlanDescriptors), nil
}
