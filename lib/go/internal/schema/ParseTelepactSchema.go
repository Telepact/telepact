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
	"encoding/json"
	"sort"
	"strings"

	"github.com/telepact/telepact/lib/go/internal/types"
)

// ParseTelepactSchema parses the provided Telepact schema documents into their structured representation.
func ParseTelepactSchema(telepactSchemaDocumentNamesToJSON map[string]string) (*ParsedSchemaResult, error) {
	if telepactSchemaDocumentNamesToJSON == nil {
		return nil, nil
	}

	originalSchema := make(map[string]any)
	parsedTypes := make(map[string]types.TType)
	fnErrorRegexes := make(map[string]string)
	parseFailures := make([]*SchemaParseFailure, 0)
	failedTypes := make(map[string]struct{})
	schemaKeysToDocumentNames := make(map[string]string)
	schemaKeysToIndex := make(map[string]int)
	schemaKeys := make(map[string]struct{})

	orderedDocumentNames := make([]string, 0, len(telepactSchemaDocumentNamesToJSON))
	for documentName := range telepactSchemaDocumentNamesToJSON {
		orderedDocumentNames = append(orderedDocumentNames, documentName)
	}
	sort.Strings(orderedDocumentNames)

	documentNameToPseudoJSON := make(map[string][]any, len(telepactSchemaDocumentNamesToJSON))

	for documentName, schemaJSON := range telepactSchemaDocumentNamesToJSON {
		var parsed any
		if err := json.Unmarshal([]byte(schemaJSON), &parsed); err != nil {
			failure := NewSchemaParseFailure(documentName, []any{}, "JsonInvalid", map[string]any{})
			return nil, &ParseError{Failures: []*SchemaParseFailure{failure}, DocumentJSON: telepactSchemaDocumentNamesToJSON}
		}

		pseudoJSON, ok := parsed.([]any)
		if !ok {
			failures := GetTypeUnexpectedParseFailure(documentName, []any{}, parsed, "Array")
			return nil, &ParseError{Failures: failures, DocumentJSON: telepactSchemaDocumentNamesToJSON}
		}

		documentNameToPseudoJSON[documentName] = pseudoJSON
	}

	for _, documentName := range orderedDocumentNames {
		pseudoJSON := documentNameToPseudoJSON[documentName]

		for index, definitionRaw := range pseudoJSON {
			loopPath := []any{index}
			definition, ok := definitionRaw.(map[string]any)
			if !ok {
				failures := GetTypeUnexpectedParseFailure(documentName, loopPath, definitionRaw, "Object")
				parseFailures = append(parseFailures, failures...)
				continue
			}

			schemaKey, err := FindSchemaKey(documentName, definition, index, telepactSchemaDocumentNamesToJSON)
			if err != nil {
				if parseErr, ok := err.(*ParseError); ok {
					parseFailures = append(parseFailures, parseErr.Failures...)
				} else {
					return nil, err
				}
				continue
			}

			matchingKey := FindMatchingSchemaKey(schemaKeys, schemaKey)
			if matchingKey != "" {
				otherIndex := schemaKeysToIndex[matchingKey]
				otherDocumentName := schemaKeysToDocumentNames[matchingKey]
				finalPath := append(append([]any{}, loopPath...), schemaKey)
				otherFinalPath := []any{otherIndex, matchingKey}
				otherDocumentJSON := telepactSchemaDocumentNamesToJSON[otherDocumentName]
				otherLocation := GetPathDocumentCoordinatesPseudoJSON(otherFinalPath, otherDocumentJSON)

				parseFailures = append(parseFailures, NewSchemaParseFailure(
					documentName,
					finalPath,
					"PathCollision",
					map[string]any{
						"document": otherDocumentName,
						"path":     otherFinalPath,
						"location": otherLocation,
					},
				))
				continue
			}

			schemaKeys[schemaKey] = struct{}{}
			schemaKeysToIndex[schemaKey] = index
			schemaKeysToDocumentNames[schemaKey] = documentName

			if documentName == "auto_" || documentName == "auth_" || !strings.HasSuffix(documentName, "_") {
				originalSchema[schemaKey] = definition
			}
		}
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: telepactSchemaDocumentNamesToJSON}
	}

	headerKeys := make(map[string]struct{})
	errorKeys := make(map[string]struct{})

	for schemaKey := range schemaKeys {
		switch {
		case strings.HasPrefix(schemaKey, "info."):
			continue
		case strings.HasPrefix(schemaKey, "headers."):
			headerKeys[schemaKey] = struct{}{}
		case strings.HasPrefix(schemaKey, "errors."):
			errorKeys[schemaKey] = struct{}{}
		default:
			index := schemaKeysToIndex[schemaKey]
			documentName := schemaKeysToDocumentNames[schemaKey]

			ctx := &ParseContext{
				DocumentName:                        documentName,
				TelepactSchemaDocumentsToPseudoJSON: documentNameToPseudoJSON,
				TelepactSchemaDocumentNamesToJSON:   telepactSchemaDocumentNamesToJSON,
				SchemaKeysToDocumentName:            schemaKeysToDocumentNames,
				SchemaKeysToIndex:                   schemaKeysToIndex,
				ParsedTypes:                         parsedTypes,
				FnErrorRegexes:                      fnErrorRegexes,
				AllParseFailures:                    &parseFailures,
				FailedTypes:                         failedTypes,
			}

			if _, err := GetOrParseType([]any{index}, schemaKey, ctx); err != nil {
				if parseErr, ok := err.(*ParseError); ok {
					parseFailures = append(parseFailures, parseErr.Failures...)
				} else {
					return nil, err
				}
			}
		}
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: telepactSchemaDocumentNamesToJSON}
	}

	errorsList := make([]*types.TError, 0, len(errorKeys))

	for errorKey := range errorKeys {
		index := schemaKeysToIndex[errorKey]
		documentName := schemaKeysToDocumentNames[errorKey]
		pseudoJSON := documentNameToPseudoJSON[documentName]
		if index < 0 || index >= len(pseudoJSON) {
			continue
		}

		definitionRaw := pseudoJSON[index]
		definition, ok := definitionRaw.(map[string]any)
		if !ok {
			failures := GetTypeUnexpectedParseFailure(documentName, []any{index}, definitionRaw, "Object")
			parseFailures = append(parseFailures, failures...)
			continue
		}

		ctx := &ParseContext{
			DocumentName:                        documentName,
			TelepactSchemaDocumentsToPseudoJSON: documentNameToPseudoJSON,
			TelepactSchemaDocumentNamesToJSON:   telepactSchemaDocumentNamesToJSON,
			SchemaKeysToDocumentName:            schemaKeysToDocumentNames,
			SchemaKeysToIndex:                   schemaKeysToIndex,
			ParsedTypes:                         parsedTypes,
			FnErrorRegexes:                      fnErrorRegexes,
			AllParseFailures:                    &parseFailures,
			FailedTypes:                         failedTypes,
		}

		errorType, err := ParseErrorType([]any{index}, definition, errorKey, ctx)
		if err != nil {
			if parseErr, ok := err.(*ParseError); ok {
				parseFailures = append(parseFailures, parseErr.Failures...)
			} else {
				return nil, err
			}
			continue
		}
		if errorType != nil {
			errorsList = append(errorsList, errorType)
		}
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: telepactSchemaDocumentNamesToJSON}
	}

	errorCollisions, err := CatchErrorCollisions(documentNameToPseudoJSON, errorKeys, schemaKeysToIndex, schemaKeysToDocumentNames, telepactSchemaDocumentNamesToJSON)
	if err != nil {
		return nil, err
	}
	if len(errorCollisions) > 0 {
		parseFailures = append(parseFailures, errorCollisions...)
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: telepactSchemaDocumentNamesToJSON}
	}

	for _, errorType := range errorsList {
		failures, err := ApplyErrorToParsedTypes(errorType, parsedTypes, schemaKeysToDocumentNames, schemaKeysToIndex, telepactSchemaDocumentNamesToJSON, fnErrorRegexes)
		if err != nil {
			return nil, err
		}
		if len(failures) > 0 {
			parseFailures = append(parseFailures, failures...)
		}
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: telepactSchemaDocumentNamesToJSON}
	}

	headersList := make([]*types.THeaders, 0, len(headerKeys))

	for headerKey := range headerKeys {
		index := schemaKeysToIndex[headerKey]
		documentName := schemaKeysToDocumentNames[headerKey]
		pseudoJSON := documentNameToPseudoJSON[documentName]
		if index < 0 || index >= len(pseudoJSON) {
			continue
		}

		definitionRaw := pseudoJSON[index]
		definition, ok := definitionRaw.(map[string]any)
		if !ok {
			failures := GetTypeUnexpectedParseFailure(documentName, []any{index}, definitionRaw, "Object")
			parseFailures = append(parseFailures, failures...)
			continue
		}

		ctx := &ParseContext{
			DocumentName:                        documentName,
			TelepactSchemaDocumentsToPseudoJSON: documentNameToPseudoJSON,
			TelepactSchemaDocumentNamesToJSON:   telepactSchemaDocumentNamesToJSON,
			SchemaKeysToDocumentName:            schemaKeysToDocumentNames,
			SchemaKeysToIndex:                   schemaKeysToIndex,
			ParsedTypes:                         parsedTypes,
			FnErrorRegexes:                      fnErrorRegexes,
			AllParseFailures:                    &parseFailures,
			FailedTypes:                         failedTypes,
		}

		headerType, err := ParseHeadersType([]any{index}, definition, headerKey, ctx)
		if err != nil {
			if parseErr, ok := err.(*ParseError); ok {
				parseFailures = append(parseFailures, parseErr.Failures...)
			} else {
				return nil, err
			}
			continue
		}
		if headerType != nil {
			headersList = append(headersList, headerType)
		}
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: telepactSchemaDocumentNamesToJSON}
	}

	headerCollisions, err := CatchHeaderCollisions(documentNameToPseudoJSON, headerKeys, schemaKeysToIndex, schemaKeysToDocumentNames, telepactSchemaDocumentNamesToJSON)
	if err != nil {
		return nil, err
	}
	if len(headerCollisions) > 0 {
		parseFailures = append(parseFailures, headerCollisions...)
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: telepactSchemaDocumentNamesToJSON}
	}

	requestHeaders := make(map[string]*types.TFieldDeclaration)
	responseHeaders := make(map[string]*types.TFieldDeclaration)

	for _, header := range headersList {
		if header == nil {
			continue
		}
		for key, field := range header.RequestHeaders {
			requestHeaders[key] = field
		}
		for key, field := range header.ResponseHeaders {
			responseHeaders[key] = field
		}
	}

	originalKeys := make([]string, 0, len(originalSchema))
	for key := range originalSchema {
		originalKeys = append(originalKeys, key)
	}
	sort.Slice(originalKeys, func(i, j int) bool {
		iInfo := strings.HasPrefix(originalKeys[i], "info.")
		jInfo := strings.HasPrefix(originalKeys[j], "info.")
		if iInfo != jInfo {
			return iInfo && !jInfo
		}
		return originalKeys[i] < originalKeys[j]
	})

	finalOriginal := make([]any, 0, len(originalKeys))
	for _, key := range originalKeys {
		finalOriginal = append(finalOriginal, originalSchema[key])
	}

	return &ParsedSchemaResult{
		Original:              finalOriginal,
		Parsed:                parsedTypes,
		ParsedRequestHeaders:  requestHeaders,
		ParsedResponseHeaders: responseHeaders,
	}, nil
}
