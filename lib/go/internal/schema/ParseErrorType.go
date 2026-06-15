//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import "github.com/telepact/telepact/lib/go/internal/types"

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
