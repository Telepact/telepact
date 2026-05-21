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

import "reflect"

func UnpackDecodedBody(body map[string]any, encoding *BinaryEncoding) map[string]any {
	result := make(map[string]any, len(body))
	for key, value := range body {
		result[key] = value
	}

	for _, packedSite := range encoding.PackedSites {
		applyDecodedPackedSite(result, packedSite, encoding)
	}

	return result
}

func applyDecodedPackedSite(root map[string]any, packedSite *BinaryPackSite, encoding *BinaryEncoding) {
	var current any = root
	for _, segment := range packedSite.Path[:max(len(packedSite.Path)-1, 0)] {
		currentMap, ok := current.(map[string]any)
		if !ok {
			return
		}
		next, ok := currentMap[segment]
		if !ok {
			return
		}
		current = next
	}

	parentMap, ok := current.(map[string]any)
	if !ok || len(packedSite.Path) == 0 {
		return
	}

	value, ok := parentMap[packedSite.Path[len(packedSite.Path)-1]]
	if !ok {
		return
	}

	listValue, ok := toDecodedSlice(value)
	if !ok {
		return
	}

	unpacked, ok := unpackDecodedList(listValue, packedSite.Header, encoding)
	if !ok {
		return
	}
	parentMap[packedSite.Path[len(packedSite.Path)-1]] = unpacked
}

func unpackDecodedList(list []any, header BinaryPackHeader, encoding *BinaryEncoding) ([]any, bool) {
	if len(list) == 0 {
		return list, true
	}
	if !isPackedMarker(list[0]) {
		return nil, false
	}
	if len(list) <= 1 {
		return nil, false
	}
	if _, ok := toDecodedSlice(list[1]); !ok {
		return nil, false
	}

	result := make([]any, 0, len(list)-1)
	for i := 1; i < len(list); i++ {
		row, ok := unpackDecodedRow(list[i], header, encoding)
		if !ok {
			return nil, false
		}
		result = append(result, row)
	}
	return result, true
}

func unpackDecodedRow(value any, header BinaryPackHeader, encoding *BinaryEncoding) (map[string]any, bool) {
	row, ok := toDecodedSlice(value)
	if !ok {
		return nil, false
	}

	result := make(map[string]any, len(row))
	for index, cell := range row {
		if index+1 >= len(header) {
			continue
		}
		if isUndefinedMarker(cell) {
			continue
		}

		headerEntry := header[index+1]
		if nestedHeader, ok := headerEntry.([]any); ok {
			if len(nestedHeader) == 0 {
				continue
			}
			keyID, ok := toInt(nestedHeader[0])
			if !ok || keyID < 0 || keyID >= len(encoding.DecodeTable) {
				return nil, false
			}
			nestedMap, ok := unpackDecodedRow(cell, BinaryPackHeader(nestedHeader), encoding)
			if !ok {
				return nil, false
			}
			result[encoding.DecodeTable[keyID]] = nestedMap
		} else {
			keyID, ok := toInt(headerEntry)
			if !ok || keyID < 0 || keyID >= len(encoding.DecodeTable) {
				return nil, false
			}
			result[encoding.DecodeTable[keyID]] = cell
		}
	}

	return result, true
}

func toDecodedSlice(value any) ([]any, bool) {
	if typed, ok := value.([]any); ok {
		return typed, true
	}

	reflectValue := reflect.ValueOf(value)
	if reflectValue.Kind() != reflect.Slice {
		return nil, false
	}

	result := make([]any, reflectValue.Len())
	for i := 0; i < reflectValue.Len(); i++ {
		result[i] = reflectValue.Index(i).Interface()
	}
	return result, true
}
