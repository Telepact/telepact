//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
