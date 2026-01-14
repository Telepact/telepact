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

import "github.com/telepact/telepact/lib/go/internal/types"

// ParseHeadersType parses a headers definition into a THeaders value.
func ParseHeadersType(path []any, headersDefinition map[string]any, schemaKey string, ctx *ParseContext) (*types.THeaders, error) {
	if ctx == nil {
		return nil, nil
	}

	parseFailures := make([]*SchemaParseFailure, 0)
	requestHeaders := make(map[string]*types.TFieldDeclaration)
	responseHeaders := make(map[string]*types.TFieldDeclaration)

	thisPath := append(append([]any{}, path...), schemaKey)
	requestHeadersDef, hasRequest := headersDefinition[schemaKey]
	if !hasRequest {
		requestHeadersDef = nil
	}

	requestHeadersMap, ok := requestHeadersDef.(map[string]any)
	if !ok {
		parseFailures = append(parseFailures, GetTypeUnexpectedParseFailure(ctx.DocumentName, thisPath, requestHeadersDef, "Object")...)
	} else {
		fields, err := ParseStructFields(thisPath, requestHeadersMap, true, ctx)
		if err != nil {
			if parseErr, ok := err.(*ParseError); ok {
				parseFailures = append(parseFailures, parseErr.Failures...)
			} else {
				return nil, err
			}
		} else {
			for key, field := range fields {
				if field != nil {
					field.Optional = true
				}
				requestHeaders[key] = field
			}
		}
	}

	responseKey := "->"
	responsePath := append(append([]any{}, path...), responseKey)

	responseHeadersDef, hasResponse := headersDefinition[responseKey]
	if !hasResponse {
		parseFailures = append(parseFailures, NewSchemaParseFailure(ctx.DocumentName, responsePath, "RequiredObjectKeyMissing", map[string]any{"key": responseKey}))
	}

	responseHeadersMap, ok := responseHeadersDef.(map[string]any)
	if !ok {
		if hasResponse {
			parseFailures = append(parseFailures, GetTypeUnexpectedParseFailure(ctx.DocumentName, responsePath, responseHeadersDef, "Object")...)
		}
	} else {
		fields, err := ParseStructFields(responsePath, responseHeadersMap, true, ctx)
		if err != nil {
			if parseErr, ok := err.(*ParseError); ok {
				parseFailures = append(parseFailures, parseErr.Failures...)
			} else {
				return nil, err
			}
		} else {
			for key, field := range fields {
				if field != nil {
					field.Optional = true
				}
				responseHeaders[key] = field
			}
		}
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	return types.NewTHeaders(schemaKey, requestHeaders, responseHeaders), nil
}
