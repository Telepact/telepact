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

import "github.com/telepact/telepact/lib/go/telepact/internal/types"

// ParseStructType parses a struct type definition from pseudo JSON.
func ParseStructType(path []any, structDefinition map[string]any, schemaKey string, ignoreKeys []string, ctx *ParseContext) (*types.TStruct, error) {
	if ctx == nil {
		return nil, nil
	}

	parseFailures := make([]*SchemaParseFailure, 0)

	otherKeys := make(map[string]struct{}, len(structDefinition))
	for key := range structDefinition {
		otherKeys[key] = struct{}{}
	}

	delete(otherKeys, schemaKey)
	delete(otherKeys, "///")
	delete(otherKeys, "_ignoreIfDuplicate")
	for _, key := range ignoreKeys {
		delete(otherKeys, key)
	}

	for key := range otherKeys {
		failurePath := append(append([]any{}, path...), key)
		parseFailures = append(parseFailures, NewSchemaParseFailure(ctx.DocumentName, failurePath, "ObjectKeyDisallowed", map[string]any{}))
	}

	thisPath := append(append([]any{}, path...), schemaKey)
	defInit, ok := structDefinition[schemaKey]
	if !ok {
		defInit = nil
	}

	definition, ok := defInit.(map[string]any)
	if !ok {
		parseFailures = append(parseFailures, GetTypeUnexpectedParseFailure(ctx.DocumentName, thisPath, defInit, "Object")...)
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	fields, err := ParseStructFields(thisPath, definition, false, ctx)
	if err != nil {
		return nil, err
	}

	return types.NewTStruct(schemaKey, fields), nil
}
