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

// ParseErrorType parses an error type definition into a TError value.
func ParseErrorType(path []any, errorDefinition map[string]any, schemaKey string, ctx *ParseContext) (*types.TError, error) {
	if ctx == nil {
		return nil, nil
	}

	parseFailures := make([]*SchemaParseFailure, 0)

	otherKeys := make(map[string]struct{}, len(errorDefinition))
	for key := range errorDefinition {
		otherKeys[key] = struct{}{}
	}
	delete(otherKeys, schemaKey)
	delete(otherKeys, "///")

	for key := range otherKeys {
		failurePath := append(append([]any{}, path...), key)
		parseFailures = append(parseFailures, NewSchemaParseFailure(ctx.DocumentName, failurePath, "ObjectKeyDisallowed", map[string]any{}))
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	union, err := ParseUnionType(path, errorDefinition, schemaKey, nil, nil, ctx)
	if err != nil {
		return nil, err
	}

	return types.NewTError(schemaKey, union), nil
}
