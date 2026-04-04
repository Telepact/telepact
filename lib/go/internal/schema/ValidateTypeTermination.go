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
	"strings"

	"github.com/telepact/telepact/lib/go/internal/types"
)

func typeDeclarationTerminates(typeDeclaration *types.TTypeDeclaration, terminatingTypeNames map[string]struct{}) bool {
	if typeDeclaration == nil {
		return true
	}

	if typeDeclaration.Nullable {
		return true
	}

	switch typ := typeDeclaration.Type.(type) {
	case *types.TArray, *types.TObject:
		return true
	case *types.TStruct:
		_, ok := terminatingTypeNames[typ.Name]
		return ok
	case *types.TUnion:
		_, ok := terminatingTypeNames[typ.Name]
		return ok
	default:
		return true
	}
}

func structFieldsTerminate(fields map[string]*types.TFieldDeclaration, terminatingTypeNames map[string]struct{}) bool {
	for _, field := range fields {
		if field == nil || field.Optional {
			continue
		}
		if !typeDeclarationTerminates(field.TypeDeclaration, terminatingTypeNames) {
			return false
		}
	}
	return true
}

func typeTerminates(typeValue types.TType, terminatingTypeNames map[string]struct{}) bool {
	switch typ := typeValue.(type) {
	case *types.TStruct:
		return structFieldsTerminate(typ.Fields, terminatingTypeNames)
	case *types.TUnion:
		for _, tag := range typ.Tags {
			if structFieldsTerminate(tag.Fields, terminatingTypeNames) {
				return true
			}
		}
		return false
	default:
		return true
	}
}

func ValidateTypeTermination(
	parsedTypes map[string]types.TType,
	schemaKeysToDocumentNames map[string]string,
	schemaKeysToIndex map[string]int,
	telepactSchemaDocumentNamesToJSON map[string]string,
) error {
	terminatingTypeNames := make(map[string]struct{})

	changed := true
	for changed {
		changed = false
		for typeName, typeValue := range parsedTypes {
			if _, ok := terminatingTypeNames[typeName]; ok {
				continue
			}
			if typeTerminates(typeValue, terminatingTypeNames) {
				terminatingTypeNames[typeName] = struct{}{}
				changed = true
			}
		}
	}

	parseFailures := make([]*SchemaParseFailure, 0)
	for schemaKey, documentName := range schemaKeysToDocumentNames {
		if strings.HasPrefix(schemaKey, "info.") || strings.HasPrefix(schemaKey, "headers.") || strings.HasPrefix(schemaKey, "errors.") {
			continue
		}

		rootTypeNames := []string{schemaKey}
		if strings.HasPrefix(schemaKey, "fn.") {
			rootTypeNames = append(rootTypeNames, schemaKey+".->")
		}

		for _, rootTypeName := range rootTypeNames {
			if _, ok := parsedTypes[rootTypeName]; ok {
				if _, ok := terminatingTypeNames[rootTypeName]; !ok {
					path := []any{schemaKeysToIndex[schemaKey], schemaKey}
					if strings.HasSuffix(rootTypeName, ".->") {
						path = []any{schemaKeysToIndex[schemaKey], "->"}
					}
					parseFailures = append(parseFailures, NewSchemaParseFailure(
						documentName,
						path,
						"RecursiveTypeUnterminated",
						map[string]any{},
					))
				}
			}
		}
	}

	if len(parseFailures) > 0 {
		return &ParseError{Failures: parseFailures, DocumentJSON: telepactSchemaDocumentNamesToJSON}
	}

	return nil
}
