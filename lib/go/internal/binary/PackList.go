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

import "github.com/vmihailenco/msgpack/v5"

const (
	// PackedByte is the msgpack extension type used to denote a packed list header.
	PackedByte byte = 17
	// UndefinedByte is the msgpack extension type used for undefined cells in packed rows.
	UndefinedByte byte = 18
)

var (
	packedListMarker = &packedListExt{}
	undefinedMarker  = &undefinedExt{}
)

type packedListExt struct{}

func (p *packedListExt) MarshalMsgpack() ([]byte, error) {
	return nil, nil
}

func (p *packedListExt) UnmarshalMsgpack([]byte) error {
	return nil
}

type undefinedExt struct{}

func (u *undefinedExt) MarshalMsgpack() ([]byte, error) {
	return nil, nil
}

func (u *undefinedExt) UnmarshalMsgpack([]byte) error {
	return nil
}

func init() {
	msgpack.RegisterExt(int8(PackedByte), (*packedListExt)(nil))
	msgpack.RegisterExt(int8(UndefinedByte), (*undefinedExt)(nil))
}

// PackList packs a list of maps using a precomputed header.
func PackList(lst []any, headers ...BinaryPackHeader) ([]any, error) {
	if len(lst) == 0 || len(headers) == 0 {
		return lst, nil
	}

	header := headers[0]
	packedList := []any{packedListMarker}
	for _, item := range lst {
		mapValue, ok := toIntKeyMap(item)
		if !ok {
			return lst, nil
		}

		row, ok, err := packRow(mapValue, header)
		if err != nil {
			return nil, err
		}
		if !ok {
			return lst, nil
		}
		packedList = append(packedList, row)
	}

	return packedList, nil
}

func packRow(m map[int]any, header BinaryPackHeader) ([]any, bool, error) {
	row := make([]any, len(header)-1)
	expectedKeys := make(map[int]struct{}, len(header)-1)
	for i := 1; i < len(header); i++ {
		headerEntry := header[i]
		keyAny := headerEntry
		if nestedHeader, ok := headerEntry.([]any); ok && len(nestedHeader) > 0 {
			keyAny = nestedHeader[0]
		}
		key, ok := toInt(keyAny)
		if !ok {
			return nil, false, nil
		}
		expectedKeys[key] = struct{}{}

		value, ok := m[key]
		if !ok {
			row[i-1] = undefinedMarker
			continue
		}

		if nestedHeader, ok := headerEntry.([]any); ok {
			nestedMap, ok := toIntKeyMap(value)
			if !ok {
				return nil, false, nil
			}
			packedValue, nestedOk, err := packRow(nestedMap, BinaryPackHeader(nestedHeader))
			if err != nil {
				return nil, false, err
			}
			if !nestedOk {
				return nil, false, nil
			}
			row[i-1] = packedValue
		} else {
			row[i-1] = value
		}
	}

	for key := range m {
		if _, ok := expectedKeys[key]; !ok {
			return nil, false, nil
		}
	}

	for len(row) > 0 {
		if _, ok := row[len(row)-1].(*undefinedExt); ok {
			row = row[:len(row)-1]
			continue
		}
		break
	}

	return row, true, nil
}

func toIntKeyMap(value any) (map[int]any, bool) {
	switch typed := value.(type) {
	case map[int]any:
		return typed, true
	case map[int64]any:
		result := make(map[int]any, len(typed))
		for key, val := range typed {
			result[int(key)] = val
		}
		return result, true
	case map[int32]any:
		result := make(map[int]any, len(typed))
		for key, val := range typed {
			result[int(key)] = val
		}
		return result, true
	case map[any]any:
		result := make(map[int]any, len(typed))
		for key, val := range typed {
			intKey, ok := toInt(key)
			if !ok {
				return nil, false
			}
			result[intKey] = val
		}
		return result, true
	default:
		return nil, false
	}
}
