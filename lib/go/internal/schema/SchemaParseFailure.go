//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

// SchemaParseFailure captures the context of a schema parsing error.
type SchemaParseFailure struct {
	DocumentName string
	Path         []any
	Reason       string
	Data         map[string]any
}

// NewSchemaParseFailure constructs a SchemaParseFailure.
func NewSchemaParseFailure(documentName string, path []any, reason string, data map[string]any) *SchemaParseFailure {
	copiedPath := append([]any(nil), path...)
	copiedData := make(map[string]any, len(data))
	for k, v := range data {
		copiedData[k] = v
	}
	return &SchemaParseFailure{
		DocumentName: documentName,
		Path:         copiedPath,
		Reason:       reason,
		Data:         copiedData,
	}
}
