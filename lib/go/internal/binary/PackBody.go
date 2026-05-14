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

// PackBody packs the message body map into the compact binary representation when possible.
func PackBody(body map[any]any, encoding *BinaryEncoding) (map[any]any, error) {
	result := make(map[any]any, len(body))
	for key, value := range body {
		result[key] = value
	}

	for _, packedSite := range encoding.PackedSites {
		parentMap, ok := getParentMap(result, packedSite.EncodedPath)
		if !ok || len(packedSite.EncodedPath) == 0 {
			continue
		}
		targetKey := packedSite.EncodedPath[len(packedSite.EncodedPath)-1]
		value, ok := parentMap[targetKey]
		if !ok {
			continue
		}
		listValue, ok := toAnySlice(value)
		if !ok {
			continue
		}
		packedValue, err := PackList(listValue, packedSite.Header)
		if err != nil {
			return nil, err
		}
		parentMap[targetKey] = packedValue
	}

	return result, nil
}

func getParentMap(root map[any]any, path []int) (map[any]any, bool) {
	current := root
	for _, key := range path[:max(len(path)-1, 0)] {
		nextValue, ok := current[key]
		if !ok {
			return nil, false
		}
		nextMap, err := ensureAnyMap(nextValue)
		if err != nil {
			return nil, false
		}
		current[key] = nextMap
		current = nextMap
	}
	if current == nil {
		return nil, false
	}
	return current, true
}

func toAnySlice(value any) ([]any, bool) {
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
