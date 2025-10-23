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
	"regexp"

	"github.com/telepact/telepact/lib/go/telepact/internal/types"
)

// ParseTypeDeclaration converts a JSON-serialised type declaration into a Telepact declaration structure.
func ParseTypeDeclaration(path []any, typeDeclarationObject any, ctx *ParseContext) (*types.TTypeDeclaration, error) {
	if ctx == nil {
		return nil, nil
	}

	switch typed := typeDeclarationObject.(type) {
	case string:
		regex := regexp.MustCompile(`^(.*?)(\?)?$`)
		matches := regex.FindStringSubmatch(typed)
		if matches == nil {
			failure := NewSchemaParseFailure(ctx.DocumentName, append([]any{}, path...), "StringRegexMatchFailed", map[string]any{"regex": regex.String()})
			return nil, &ParseError{Failures: []*SchemaParseFailure{failure}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
		}

		typeName := matches[1]
		nullable := matches[2] != ""

		resolvedType, err := GetOrParseType(append([]any{}, path...), typeName, ctx)
		if err != nil {
			return nil, err
		}
		if resolvedType == nil {
			return nil, nil
		}

		if resolvedType.GetTypeParameterCount() != 0 {
			failure := NewSchemaParseFailure(ctx.DocumentName, append([]any{}, path...), "ArrayLengthUnexpected", map[string]any{
				"actual":   1,
				"expected": resolvedType.GetTypeParameterCount() + 1,
			})
			return nil, &ParseError{Failures: []*SchemaParseFailure{failure}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
		}

		return types.NewTTypeDeclaration(resolvedType, nullable, nil), nil

	case []any:
		if len(typed) != 1 {
			failure := NewSchemaParseFailure(ctx.DocumentName, append([]any{}, path...), "ArrayLengthUnexpected", map[string]any{
				"actual":   len(typed),
				"expected": 1,
			})
			return nil, &ParseError{Failures: []*SchemaParseFailure{failure}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
		}

		elementPath := append(append([]any{}, path...), 0)
		elementDeclaration, err := ParseTypeDeclaration(elementPath, typed[0], ctx)
		if err != nil {
			return nil, err
		}

		return types.NewTTypeDeclaration(types.NewTArray(), false, []*types.TTypeDeclaration{elementDeclaration}), nil

	case map[string]any:
		if len(typed) != 1 {
			failure := NewSchemaParseFailure(ctx.DocumentName, append([]any{}, path...), "ObjectSizeUnexpected", map[string]any{
				"actual":   len(typed),
				"expected": 1,
			})
			return nil, &ParseError{Failures: []*SchemaParseFailure{failure}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
		}

		var key string
		var value any
		for k, v := range typed {
			key = k
			value = v
			break
		}

		if key != "string" {
			failureMissing := NewSchemaParseFailure(ctx.DocumentName, append([]any{}, path...), "RequiredObjectKeyMissing", map[string]any{"key": "string"})
			keyPath := append(append([]any{}, path...), key)
			failureDisallowed := NewSchemaParseFailure(ctx.DocumentName, keyPath, "ObjectKeyDisallowed", map[string]any{})
			return nil, &ParseError{Failures: []*SchemaParseFailure{failureMissing, failureDisallowed}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
		}

		valuePath := append(append([]any{}, path...), key)
		valueDeclaration, err := ParseTypeDeclaration(valuePath, value, ctx)
		if err != nil {
			return nil, err
		}

		return types.NewTTypeDeclaration(types.NewTObject(), false, []*types.TTypeDeclaration{valueDeclaration}), nil

	default:
		failures := GetTypeUnexpectedParseFailure(ctx.DocumentName, append([]any{}, path...), typeDeclarationObject, "StringOrArrayOrObject")
		return nil, &ParseError{Failures: failures, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}
}
