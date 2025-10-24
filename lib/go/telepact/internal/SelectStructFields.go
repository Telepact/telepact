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

package internal

import (
	"fmt"
	"strings"

	"github.com/telepact/telepact/lib/go/telepact/internal/types"
)

// SelectStructFields filters a value based on the provided type declaration and select structure.
func SelectStructFields(typeDeclaration *types.TTypeDeclaration, value any, selectedStructFields map[string]any) any {
	if typeDeclaration == nil {
		return value
	}

	switch typed := typeDeclaration.Type.(type) {
	case *types.TStruct:
		valueMap := toStringAnyMap(value)
		structName := typed.Name
		selectedFields := toStringSlice(getSelectEntry(selectedStructFields, structName))

		result := make(map[string]any)
		for fieldName, fieldValue := range valueMap {
			if selectedFields != nil && !containsString(selectedFields, fieldName) {
				continue
			}

			fieldDecl := typed.Fields[fieldName]
			if fieldDecl == nil {
				continue
			}

			result[fieldName] = SelectStructFields(fieldDecl.TypeDeclaration, fieldValue, selectedStructFields)
		}
		return result

	case *types.TUnion:
		valueMap := toStringAnyMap(value)
		unionTag := firstKey(valueMap)
		unionData := toStringAnyMap(valueMap[unionTag])

		defaultTagSelections := make(map[string][]string, len(typed.Tags))
		for tagKey, unionStruct := range typed.Tags {
			fieldNames := make([]string, 0, len(unionStruct.Fields))
			for fieldName := range unionStruct.Fields {
				fieldNames = append(fieldNames, fieldName)
			}
			defaultTagSelections[tagKey] = fieldNames
		}

		unionSelectedRaw := getSelectEntry(selectedStructFields, typed.Name)
		unionSelected := toMapOfStringToInterface(unionSelectedRaw)
		if len(unionSelected) == 0 {
			for tagKey, fieldNames := range defaultTagSelections {
				converted := make([]any, len(fieldNames))
				for i, fieldName := range fieldNames {
					converted[i] = fieldName
				}
				unionSelected[tagKey] = converted
			}
		}

		selectedFields := defaultTagSelections[unionTag]
		if rawSelected, ok := unionSelected[unionTag]; ok {
			selectedFields = toStringSlice(rawSelected)
		}

		result := make(map[string]any)
		unionStruct := typed.Tags[unionTag]
		if unionStruct == nil {
			return map[string]any{unionTag: result}
		}

		for fieldName, fieldValue := range unionData {
			if selectedFields != nil && !containsString(selectedFields, fieldName) {
				continue
			}
			fieldDecl := unionStruct.Fields[fieldName]
			if fieldDecl == nil {
				continue
			}
			result[fieldName] = SelectStructFields(fieldDecl.TypeDeclaration, fieldValue, selectedStructFields)
		}

		return map[string]any{unionTag: result}

	case *types.TObject:
		valueMap := toStringAnyMap(value)
		if len(typeDeclaration.TypeParameters) == 0 {
			return valueMap
		}

		nestedType := typeDeclaration.TypeParameters[0]
		result := make(map[string]any, len(valueMap))
		for key, entry := range valueMap {
			result[key] = SelectStructFields(nestedType, entry, selectedStructFields)
		}
		return result

	case *types.TArray:
		if len(typeDeclaration.TypeParameters) == 0 {
			return value
		}
		nestedType := typeDeclaration.TypeParameters[0]
		valueSlice := toAnySlice(value)
		result := make([]any, 0, len(valueSlice))
		for _, entry := range valueSlice {
			result = append(result, SelectStructFields(nestedType, entry, selectedStructFields))
		}
		return result

	default:
		return value
	}
}

func toStringAnyMap(value any) map[string]any {
	switch typed := value.(type) {
	case map[string]any:
		return typed
	case map[any]any:
		result := make(map[string]any, len(typed))
		for key, val := range typed {
			result[toString(key)] = val
		}
		return result
	default:
		return map[string]any{}
	}
}

func getSelectEntry(selected map[string]any, key string) any {
	if selected == nil {
		return nil
	}
	if value, ok := selected[key]; ok {
		return value
	}
	if strings.HasPrefix(key, "fn.") && strings.HasSuffix(key, ".->") {
		if value, ok := selected["->"]; ok {
			return value
		}
	}
	return nil
}

func toAnySlice(value any) []any {
	switch typed := value.(type) {
	case []any:
		return typed
	case []string:
		result := make([]any, len(typed))
		for i, entry := range typed {
			result[i] = entry
		}
		return result
	default:
		return []any{}
	}
}

func toStringSlice(value any) []string {
	switch typed := value.(type) {
	case []string:
		return typed
	case []any:
		result := make([]string, 0, len(typed))
		for _, entry := range typed {
			if str, ok := entry.(string); ok {
				result = append(result, str)
			}
		}
		return result
	default:
		return nil
	}
}

func toMapOfStringToInterface(value any) map[string]any {
	switch typed := value.(type) {
	case map[string]any:
		return typed
	case map[any]any:
		result := make(map[string]any, len(typed))
		for key, val := range typed {
			result[toString(key)] = val
		}
		return result
	default:
		return map[string]any{}
	}
}

func containsString(slice []string, target string) bool {
	for _, entry := range slice {
		if entry == target {
			return true
		}
	}
	return false
}

func firstKey(m map[string]any) string {
	for key := range m {
		return key
	}
	return ""
}

func toString(value any) string {
	switch v := value.(type) {
	case string:
		return v
	case fmt.Stringer:
		return v.String()
	default:
		return fmt.Sprintf("%v", v)
	}
}
