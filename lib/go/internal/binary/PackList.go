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

import (
	"errors"

	"github.com/vmihailenco/msgpack/v5"
)

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

// PackList attempts to pack a list of maps into the compact representation used by the Telepact binary encoder.
func PackList(lst []any) ([]any, error) {
	if len(lst) == 0 {
		return lst, nil
	}

	header := []any{nil}
	packedList := []any{packedListMarker, header}
	keyIndexMap := make(map[int]*BinaryPackNode)

	for _, item := range lst {
		mapValue, ok := toIntKeyMap(item)
		if !ok {
			return fallbackPackList(lst)
		}

		row, err := PackMap(mapValue, &header, keyIndexMap)
		if err != nil {
			var cannotPack CannotPack
			if errors.As(err, &cannotPack) {
				return fallbackPackList(lst)
			}
			return nil, err
		}

		packedList = append(packedList, row)
	}

	packedList[1] = header
	return packedList, nil
}

func fallbackPackList(lst []any) ([]any, error) {
	result := make([]any, len(lst))
	for i, item := range lst {
		packed, err := Pack(item)
		if err != nil {
			return nil, err
		}
		result[i] = packed
	}
	return result, nil
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
