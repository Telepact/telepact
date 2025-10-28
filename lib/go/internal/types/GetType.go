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

package types

import "reflect"

// GetType mirrors the Python helper by mapping runtime values to schema type names.
func GetType(value any) string {
	if value == nil {
		return nullName
	}

	switch value.(type) {
	case bool:
		return booleanName
	case int, int8, int16, int32, int64:
		return numberName
	case uint, uint8, uint16, uint32, uint64:
		return numberName
	case float32, float64:
		return numberName
	case string:
		return stringName
	case []byte:
		return stringName
	case map[string]any:
		return objectName
	case []any:
		return arrayName
	}

	typeOfValue := reflect.TypeOf(value)
	if typeOfValue.Kind() == reflect.Map {
		return objectName
	}
	if typeOfValue.Kind() == reflect.Slice || typeOfValue.Kind() == reflect.Array {
		return arrayName
	}
	return "Unknown"
}
