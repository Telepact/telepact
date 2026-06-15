//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import (
	"regexp"
	"strings"

	"github.com/telepact/telepact/lib/go/internal/types"
)

// ApplyErrorToParsedTypes attaches the supplied error struct to parsed function result unions.
// It returns any schema parse failures encountered so the caller can surface them appropriately.
func ApplyErrorToParsedTypes(
	errorType *types.TError,
	parsedTypes map[string]types.TType,
	schemaKeysToDocumentNames map[string]string,
	schemaKeysToIndex map[string]int,
	documentNamesToJSON map[string]string,
	fnErrorRegexes map[string]string,
) ([]*SchemaParseFailure, error) {
	if errorType == nil || errorType.Errors == nil {
		return nil, nil
	}

	parseFailures := make([]*SchemaParseFailure, 0)

	errorKey := errorType.Name
	errorIndex := schemaKeysToIndex[errorKey]
	documentName := schemaKeysToDocumentNames[errorKey]

	for parsedTypeName := range parsedTypes {
		if !strings.HasPrefix(parsedTypeName, "fn.") || strings.HasSuffix(parsedTypeName, ".->") {
			continue
		}

		fnName := parsedTypeName
		resultTypeKey := fnName + ".->"
		parsedResultType, ok := parsedTypes[resultTypeKey]
		if !ok {
			continue
		}

		fnUnion, ok := parsedResultType.(*types.TUnion)
		if !ok || fnUnion == nil {
			continue
		}

		fnErrorRegex, hasRegex := fnErrorRegexes[fnName]
		if !hasRegex || fnErrorRegex == "" {
			continue
		}

		regex := regexp.MustCompile(fnErrorRegex)
		if !regex.MatchString(errorKey) {
			continue
		}

		fnResultTags := fnUnion.Tags
		errorTags := errorType.Errors.Tags

		for errorTagName, errorTag := range errorTags {
			if _, exists := fnResultTags[errorTagName]; exists {
				otherPathIndex := schemaKeysToIndex[fnName]
				errorTagIndex := errorType.Errors.TagIndices[errorTagName]
				otherDocumentName := schemaKeysToDocumentNames[fnName]
				fnErrorTagIndex := fnUnion.TagIndices[errorTagName]
				otherFinalPath := []any{otherPathIndex, "->", fnErrorTagIndex, errorTagName}
				otherLocation := ResolveDocumentCoordinates(otherFinalPath, otherDocumentName, documentNamesToJSON)

				failurePath := []any{errorIndex, errorKey, errorTagIndex, errorTagName}
				parseFailures = append(parseFailures, NewSchemaParseFailure(
					documentName,
					failurePath,
					"PathCollision",
					map[string]any{
						"document": otherDocumentName,
						"path":     otherFinalPath,
						"location": otherLocation,
					},
				))
			}

			fnResultTags[errorTagName] = errorTag
		}
	}

	return parseFailures, nil
}
