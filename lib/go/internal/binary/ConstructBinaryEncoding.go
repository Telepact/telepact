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
	packSites := make([]any, 0)

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
			for fieldKey, field := range resultStruct.Fields {
				packSites = collectPackSites(field.TypeDeclaration, []string{"Ok_", fieldKey}, packSites, map[string]struct{}{}, false)
			}
		} else if strings.HasPrefix(key, "fn.") {
			allKeys[key] = struct{}{}

			argsStruct, ok := unionType.Tags[key]
			if !ok {
				continue
			}

			appendStructKeys(argsStruct.Fields, allKeys)
			for fieldKey, field := range argsStruct.Fields {
				packSites = collectPackSites(field.TypeDeclaration, []string{key, fieldKey}, packSites, map[string]struct{}{}, false)
			}
		}
	}

	sortedKeys := make([]string, 0, len(allKeys))
	for key := range allKeys {
		sortedKeys = append(sortedKeys, key)
	}
	sort.Strings(sortedKeys)

	encodingMap := make(map[string]int, len(sortedKeys))
	for index, key := range sortedKeys {
		encodingMap[key] = index
	}

	checksum := CreateChecksum(strings.Join(sortedKeys, "\n"))
	return NewBinaryEncoding(encodingMap, checksum, packSites), nil
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
	case *types.TAny:
		return keys
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

func buildPackHeader(typeDeclaration *types.TTypeDeclaration, rootKey any) []any {
	header := []any{rootKey}
	structType, ok := typeDeclaration.Type.(*types.TStruct)
	if !ok {
		return header
	}
	for fieldKey, field := range structType.Fields {
		if _, ok := field.TypeDeclaration.Type.(*types.TStruct); ok {
			header = append(header, buildPackHeader(field.TypeDeclaration, fieldKey))
			continue
		}
		header = append(header, fieldKey)
	}
	return header
}

func collectPackSites(typeDeclaration *types.TTypeDeclaration, path []string, packSites []any, activeTypeNames map[string]struct{}, underGenericList bool) []any {
	switch typed := typeDeclaration.Type.(type) {
	case *types.TArray:
		if len(typeDeclaration.TypeParameters) == 0 {
			return packSites
		}
		itemType := typeDeclaration.TypeParameters[0]
		if !underGenericList {
			if _, ok := itemType.Type.(*types.TStruct); ok {
				return append(packSites, []any{stringSliceToAny(path), buildPackHeader(itemType, nil)})
			}
		}
		return collectPackSites(itemType, path, packSites, activeTypeNames, true)
	case *types.TAny, *types.TObject:
		return packSites
	case *types.TStruct:
		if _, seen := activeTypeNames[typed.Name]; seen {
			return packSites
		}
		nextActive := copyStringSet(activeTypeNames)
		nextActive[typed.Name] = struct{}{}
		for fieldKey, field := range typed.Fields {
			packSites = collectPackSites(field.TypeDeclaration, append(append([]string{}, path...), fieldKey), packSites, nextActive, underGenericList)
		}
		return packSites
	case *types.TUnion:
		if _, seen := activeTypeNames[typed.Name]; seen {
			return packSites
		}
		nextActive := copyStringSet(activeTypeNames)
		nextActive[typed.Name] = struct{}{}
		for tagKey, tagStruct := range typed.Tags {
			for fieldKey, field := range tagStruct.Fields {
				packSites = collectPackSites(field.TypeDeclaration, append(append([]string{}, path...), tagKey, fieldKey), packSites, nextActive, underGenericList)
			}
		}
		return packSites
	default:
		return packSites
	}
}

func copyStringSet(src map[string]struct{}) map[string]struct{} {
	dst := make(map[string]struct{}, len(src))
	for key := range src {
		dst[key] = struct{}{}
	}
	return dst
}

func stringSliceToAny(value []string) []any {
	result := make([]any, len(value))
	for i, entry := range value {
		result[i] = entry
	}
	return result
}
