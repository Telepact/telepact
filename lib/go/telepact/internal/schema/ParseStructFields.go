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

	"github.com/telepact/telepact/lib/go/telepact/internal/types"
)

// ParseStructFields parses field declarations for structs and headers.
func ParseStructFields(path []any, referenceStruct map[string]any, isHeader bool, ctx *ParseContext) (map[string]*types.TFieldDeclaration, error) {
	if ctx == nil {
		return nil, nil
	}

	parseFailures := make([]*SchemaParseFailure, 0)
	fields := make(map[string]*types.TFieldDeclaration)

	for fieldDeclaration, typeDeclarationValue := range referenceStruct {
		for existingField := range fields {
			existingFieldNoOpt := strings.Split(existingField, "!")[0]
			fieldNoOpt := strings.Split(fieldDeclaration, "!")[0]
			if existingFieldNoOpt == fieldNoOpt {
				finalPath := append(append([]any{}, path...), fieldDeclaration)
				otherPath := append(append([]any{}, path...), existingField)
				documentJSON := ctx.TelepactSchemaDocumentNamesToJSON[ctx.DocumentName]
				otherLocation := GetPathDocumentCoordinatesPseudoJSON(otherPath, documentJSON)

				parseFailures = append(parseFailures, NewSchemaParseFailure(
					ctx.DocumentName,
					finalPath,
					"PathCollision",
					map[string]any{
						"document": ctx.DocumentName,
						"path":     otherPath,
						"location": otherLocation,
					},
				))
			}
		}

		parsedField, err := ParseField(path, fieldDeclaration, typeDeclarationValue, isHeader, ctx)
		if err != nil {
			if parseErr, ok := err.(*ParseError); ok {
				parseFailures = append(parseFailures, parseErr.Failures...)
			} else {
				return nil, err
			}
			continue
		}
		if parsedField == nil {
			continue
		}
		fields[parsedField.FieldName] = parsedField
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	return fields, nil
}
