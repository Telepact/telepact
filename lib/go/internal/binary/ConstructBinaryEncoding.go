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
	"sort"
	"strings"

	"github.com/telepact/telepact/lib/go/internal/types"
)

// ConstructBinaryEncoding builds a BinaryEncoding from the supplied parsed Telepact schema types.
func ConstructBinaryEncoding(parsed map[string]types.TType) (*BinaryEncoding, error) {
	allKeys := make(map[string]struct{})
	requestPlanDescriptors := make([]any, 0)
	responsePlanDescriptors := make([]any, 0)

	functionKeys := make([]string, 0)
	for key, value := range parsed {
		unionType, ok := value.(*types.TUnion)
		if !ok {
			continue
		}

		if strings.HasSuffix(key, ".->") {
			resultStruct, ok := unionType.Tags["Ok_"]
			if !ok {
				continue
			}

			allKeys["Ok_"] = struct{}{}
			appendStructKeys(resultStruct.Fields, allKeys)
		} else if strings.HasPrefix(key, "fn.") {
			allKeys[key] = struct{}{}
			functionKeys = append(functionKeys, key)

			argsStruct, ok := unionType.Tags[key]
			if !ok {
				continue
			}

			appendStructKeys(argsStruct.Fields, allKeys)
		}
	}
	sort.Strings(functionKeys)

	sortedKeys := make([]string, 0, len(allKeys))
	for key := range allKeys {
		sortedKeys = append(sortedKeys, key)
	}
	sort.Strings(sortedKeys)

	encodingMap := make(map[string]int, len(sortedKeys))
	for index, key := range sortedKeys {
		encodingMap[key] = index
	}

	for _, key := range functionKeys {
		value := parsed[key]
		unionType, ok := value.(*types.TUnion)
		if !ok || !strings.HasPrefix(key, "fn.") {
			continue
		}
		responseType, ok := parsed[key+".->"].(*types.TUnion)
		if !ok {
			continue
		}

		argsStruct, ok := unionType.Tags[key]
		if !ok {
			continue
		}
		requestPlanDescriptors = append(requestPlanDescriptors, []any{
			encodingMap[key],
			map[string]any{
				"t": "s",
				"f": compileStructDescriptor(argsStruct.Fields, encodingMap),
			},
		})

		resultStruct, ok := responseType.Tags["Ok_"]
		if !ok {
			continue
		}
		responsePlanDescriptors = append(responsePlanDescriptors, []any{
			encodingMap[key],
			map[string]any{
				"t": "s",
				"f": compileStructDescriptor(resultStruct.Fields, encodingMap),
			},
		})
	}

	checksum := CreateChecksum(strings.Join(sortedKeys, "\n"))
	return NewBinaryEncoding(encodingMap, checksum, sortedKeys, requestPlanDescriptors, responsePlanDescriptors), nil
}

func compileStructDescriptor(fields map[string]*types.TFieldDeclaration, encodeMap map[string]int) []any {
	fieldKeys := make([]string, 0, len(fields))
	for fieldKey := range fields {
		fieldKeys = append(fieldKeys, fieldKey)
	}
	sort.Strings(fieldKeys)
	result := make([]any, 0, len(fields))
	for _, fieldKey := range fieldKeys {
		field := fields[fieldKey]
		result = append(result, []any{encodeMap[fieldKey], compileTypeDescriptor(field.TypeDeclaration, encodeMap, map[string]struct{}{})})
	}
	return result
}

func compileTypeDescriptor(typeDeclaration *types.TTypeDeclaration, encodeMap map[string]int, visited map[string]struct{}) map[string]any {
	if typeDeclaration == nil {
		return map[string]any{"t": "d"}
	}

	switch typed := typeDeclaration.Type.(type) {
	case *types.TArray:
		if len(typeDeclaration.TypeParameters) == 0 {
			return map[string]any{"t": "d"}
		}
		return map[string]any{
			"t": "a",
			"i": compileTypeDescriptor(typeDeclaration.TypeParameters[0], encodeMap, visited),
		}
	case *types.TObject:
		return map[string]any{"t": "d"}
	case *types.TStruct:
		if _, ok := visited[typed.Name]; ok {
			return map[string]any{"t": "d"}
		}
		nextVisited := cloneVisited(visited)
		nextVisited[typed.Name] = struct{}{}
		return map[string]any{
			"t": "s",
			"f": compileStructDescriptorWithVisited(typed.Fields, encodeMap, nextVisited),
		}
	case *types.TUnion:
		if _, ok := visited[typed.Name]; ok {
			return map[string]any{"t": "d"}
		}
		nextVisited := cloneVisited(visited)
		nextVisited[typed.Name] = struct{}{}
		tagKeys := make([]string, 0, len(typed.Tags))
		for tagKey := range typed.Tags {
			tagKeys = append(tagKeys, tagKey)
		}
		sort.Strings(tagKeys)
		tags := make([]any, 0, len(typed.Tags))
		for _, tagKey := range tagKeys {
			tagStruct := typed.Tags[tagKey]
			tags = append(tags, []any{
				encodeMap[tagKey],
				map[string]any{
					"t": "s",
					"f": compileStructDescriptorWithVisited(tagStruct.Fields, encodeMap, nextVisited),
				},
			})
		}
		return map[string]any{"t": "u", "g": tags}
	default:
		return map[string]any{"t": "v"}
	}
}

func compileStructDescriptorWithVisited(fields map[string]*types.TFieldDeclaration, encodeMap map[string]int, visited map[string]struct{}) []any {
	fieldKeys := make([]string, 0, len(fields))
	for fieldKey := range fields {
		fieldKeys = append(fieldKeys, fieldKey)
	}
	sort.Strings(fieldKeys)
	result := make([]any, 0, len(fields))
	for _, fieldKey := range fieldKeys {
		field := fields[fieldKey]
		result = append(result, []any{encodeMap[fieldKey], compileTypeDescriptor(field.TypeDeclaration, encodeMap, visited)})
	}
	return result
}

func cloneVisited(visited map[string]struct{}) map[string]struct{} {
	cloned := make(map[string]struct{}, len(visited))
	for key, value := range visited {
		cloned[key] = value
	}
	return cloned
}

func appendStructKeys(fields map[string]*types.TFieldDeclaration, allKeys map[string]struct{}) {
	for fieldKey, field := range fields {
		allKeys[fieldKey] = struct{}{}
		for _, nestedKey := range traceType(field.TypeDeclaration) {
			allKeys[nestedKey] = struct{}{}
		}
	}
}

func traceType(typeDeclaration *types.TTypeDeclaration) []string {
	if typeDeclaration == nil {
		return nil
	}

	var keys []string

	switch typed := typeDeclaration.Type.(type) {
	case *types.TArray:
		if len(typeDeclaration.TypeParameters) > 0 {
			keys = append(keys, traceType(typeDeclaration.TypeParameters[0])...)
		}
	case *types.TObject:
		if len(typeDeclaration.TypeParameters) > 0 {
			keys = append(keys, traceType(typeDeclaration.TypeParameters[0])...)
		}
	case *types.TStruct:
		for structFieldKey, structField := range typed.Fields {
			keys = append(keys, structFieldKey)
			keys = append(keys, traceType(structField.TypeDeclaration)...)
		}
	case *types.TUnion:
		for tagKey, tagStruct := range typed.Tags {
			keys = append(keys, tagKey)
			for structFieldKey, structField := range tagStruct.Fields {
				keys = append(keys, structFieldKey)
				keys = append(keys, traceType(structField.TypeDeclaration)...)
			}
		}
	}

	return keys
}
