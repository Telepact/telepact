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

package schema

import (
	"sort"
	"strings"

	"github.com/telepact/telepact/lib/go/internal/types"
)

// DerivePossibleSelects computes the set of selectable fields for a function result union.
func DerivePossibleSelects(fnName string, result *types.TUnion) map[string]any {
	if result == nil {
		return map[string]any{}
	}

	nestedTypes := make(map[string]types.TType)
	okStruct := result.Tags["Ok_"]
	if okStruct == nil {
		return map[string]any{}
	}

	okFieldNames := make([]string, 0, len(okStruct.Fields))
	for name, fieldDecl := range okStruct.Fields {
		okFieldNames = append(okFieldNames, name)
		findNestedTypes(fieldDecl.TypeDeclaration, nestedTypes)
	}
	sort.Strings(okFieldNames)

	possibleSelect := map[string]any{
		"->": map[string]any{"Ok_": okFieldNames},
	}

	sortedTypeKeys := make([]string, 0, len(nestedTypes))
	for key := range nestedTypes {
		sortedTypeKeys = append(sortedTypeKeys, key)
	}
	sort.Strings(sortedTypeKeys)

	for _, key := range sortedTypeKeys {
		if strings.HasPrefix(key, "fn.") {
			continue
		}

		typ := nestedTypes[key]
		switch typed := typ.(type) {
		case *types.TUnion:
			unionSelect := make(map[string][]string)
			tagKeys := make([]string, 0, len(typed.Tags))
			for tagKey := range typed.Tags {
				tagKeys = append(tagKeys, tagKey)
			}
			sort.Strings(tagKeys)

			for _, tagKey := range tagKeys {
				tagStruct := typed.Tags[tagKey]
				if tagStruct == nil {
					continue
				}
				fieldNames := make([]string, 0, len(tagStruct.Fields))
				for fieldName := range tagStruct.Fields {
					fieldNames = append(fieldNames, fieldName)
				}
				sort.Strings(fieldNames)
				if len(fieldNames) > 0 {
					unionSelect[tagKey] = fieldNames
				}
			}

			if len(unionSelect) > 0 {
				possibleSelect[key] = unionSelect
			}
		case *types.TStruct:
			fieldNames := make([]string, 0, len(typed.Fields))
			for fieldName := range typed.Fields {
				fieldNames = append(fieldNames, fieldName)
			}
			sort.Strings(fieldNames)
			if len(fieldNames) > 0 {
				possibleSelect[key] = fieldNames
			}
		}
	}

	return possibleSelect
}

func findNestedTypes(typeDeclaration *types.TTypeDeclaration, nestedTypes map[string]types.TType) {
	if typeDeclaration == nil || typeDeclaration.Type == nil {
		return
	}

	switch typed := typeDeclaration.Type.(type) {
	case *types.TUnion:
		nestedTypes[typed.Name] = typed
		for _, tag := range typed.Tags {
			if tag == nil {
				continue
			}
			for _, fieldDecl := range tag.Fields {
				findNestedTypes(fieldDecl.TypeDeclaration, nestedTypes)
			}
		}
	case *types.TStruct:
		nestedTypes[typed.Name] = typed
		for _, fieldDecl := range typed.Fields {
			findNestedTypes(fieldDecl.TypeDeclaration, nestedTypes)
		}
	case *types.TArray, *types.TObject:
		if len(typeDeclaration.TypeParameters) > 0 {
			findNestedTypes(typeDeclaration.TypeParameters[0], nestedTypes)
		}
	}
}
