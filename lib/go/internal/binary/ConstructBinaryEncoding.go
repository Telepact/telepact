//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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

			argsStruct, ok := unionType.Tags[key]
			if !ok {
				continue
			}

			appendStructKeys(argsStruct.Fields, allKeys)
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
	return NewBinaryEncoding(encodingMap, checksum), nil
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
