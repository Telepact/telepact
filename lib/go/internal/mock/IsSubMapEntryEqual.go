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

package mock

import (
	"fmt"
	"reflect"
)

// IsSubMapEntryEqual determines whether a value from the expected map matches the value in the actual map.
func IsSubMapEntryEqual(partValue any, wholeValue any) bool {
	partMap, partIsMap := toStringAnyMap(partValue)
	wholeMap, wholeIsMap := toStringAnyMap(wholeValue)
	if partIsMap && wholeIsMap {
		return IsSubMap(partMap, wholeMap)
	}

	partSlice, partIsSlice := toAnySlice(partValue)
	wholeSlice, wholeIsSlice := toAnySlice(wholeValue)
	if partIsSlice && wholeIsSlice {
		for _, element := range partSlice {
			if !PartiallyMatches(wholeSlice, element) {
				return false
			}
		}
		return true
	}

	return reflect.DeepEqual(partValue, wholeValue)
}

func toStringAnyMap(value any) (map[string]any, bool) {
	switch typed := value.(type) {
	case map[string]any:
		return typed, true
	case map[any]any:
		converted := make(map[string]any, len(typed))
		for key, entry := range typed {
			converted[toString(key)] = entry
		}
		return converted, true
	default:
		return nil, false
	}
}

func toAnySlice(value any) ([]any, bool) {
	switch typed := value.(type) {
	case []any:
		return typed, true
	case []string:
		converted := make([]any, len(typed))
		for i, entry := range typed {
			converted[i] = entry
		}
		return converted, true
	case []int:
		converted := make([]any, len(typed))
		for i, entry := range typed {
			converted[i] = entry
		}
		return converted, true
	default:
		val := reflect.ValueOf(value)
		if !val.IsValid() || val.Kind() != reflect.Slice {
			return nil, false
		}

		converted := make([]any, val.Len())
		for i := 0; i < val.Len(); i++ {
			converted[i] = val.Index(i).Interface()
		}
		return converted, true
	}
}

func toString(value any) string {
	switch v := value.(type) {
	case nil:
		return "<nil>"
	case string:
		return v
	case fmt.Stringer:
		return v.String()
	default:
		return fmt.Sprintf("%v", v)
	}
}
