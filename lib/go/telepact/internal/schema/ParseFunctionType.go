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

// ParseFunctionResultType parses the result union for a function definition.
func ParseFunctionResultType(path []any, functionDefinition map[string]any, schemaKey string, ctx *ParseContext) (*types.TUnion, error) {
	if ctx == nil {
		return nil, nil
	}

	parseFailures := make([]*SchemaParseFailure, 0)
	resultSchemaKey := "->"
	resultPath := append(append([]any{}, path...), resultSchemaKey)

	var resultType *types.TUnion
	if _, exists := functionDefinition[resultSchemaKey]; !exists {
		parseFailures = append(parseFailures, NewSchemaParseFailure(ctx.DocumentName, resultPath, "RequiredObjectKeyMissing", map[string]any{"key": resultSchemaKey}))
	} else {
		ignoreKeys := make([]string, 0, len(functionDefinition))
		for key := range functionDefinition {
			ignoreKeys = append(ignoreKeys, key)
		}

		parsedResult, err := ParseUnionType(path, functionDefinition, resultSchemaKey, ignoreKeys, []string{"Ok_"}, ctx)
		if err != nil {
			if parseErr, ok := err.(*ParseError); ok {
				parseFailures = append(parseFailures, parseErr.Failures...)
			} else {
				return nil, err
			}
		} else {
			resultType = parsedResult
		}
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	fnSelectType := DerivePossibleSelects(schemaKey, resultType)
	selectTypeAny, err := GetOrParseType([]any{}, "_ext.Select_", ctx)
	if err != nil {
		return nil, err
	}

	selectType, ok := selectTypeAny.(*types.TSelect)
	if !ok {
		return nil, &ParseError{Failures: []*SchemaParseFailure{NewSchemaParseFailure(ctx.DocumentName, []any{}, "TypeExtensionImplementationMissing", map[string]any{"name": "_ext.Select_"})}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}
	if selectType.PossibleSelects == nil {
		selectType.PossibleSelects = make(map[string]any)
	}
	selectType.PossibleSelects[schemaKey] = fnSelectType

	return resultType, nil
}

// ParseFunctionErrorsRegex parses the optional errors regex for a function definition.
func ParseFunctionErrorsRegex(path []any, functionDefinition map[string]any, schemaKey string, ctx *ParseContext) (string, error) {
	if ctx == nil {
		return "", nil
	}

	parseFailures := make([]*SchemaParseFailure, 0)
	errorsRegexKey := "_errors"
	regexPath := append(append([]any{}, path...), errorsRegexKey)

	errorsRegex := "^errors\\..*$"

	if value, exists := functionDefinition[errorsRegexKey]; exists {
		if !strings.HasSuffix(schemaKey, "_") {
			parseFailures = append(parseFailures, NewSchemaParseFailure(ctx.DocumentName, regexPath, "ObjectKeyDisallowed", map[string]any{}))
		}

		if stringValue, ok := value.(string); ok {
			errorsRegex = stringValue
		} else {
			parseFailures = append(parseFailures, GetTypeUnexpectedParseFailure(ctx.DocumentName, regexPath, value, "String")...)
		}
	}

	if len(parseFailures) > 0 {
		return "", &ParseError{Failures: parseFailures, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	return errorsRegex, nil
}
