//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import "github.com/telepact/telepact/lib/go/internal/types"

// GetTypeUnexpectedParseFailure constructs a parse failure describing an unexpected type.
func GetTypeUnexpectedParseFailure(documentName string, path []any, value any, expectedType string) []*SchemaParseFailure {
	actualType := types.GetType(value)
	data := map[string]any{
		"actual":   map[string]any{actualType: map[string]any{}},
		"expected": map[string]any{expectedType: map[string]any{}},
	}

	return []*SchemaParseFailure{
		NewSchemaParseFailure(documentName, path, "TypeUnexpected", data),
	}
}
