//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import "github.com/telepact/telepact/lib/go/internal/types"

// ParseContext carries contextual information shared across schema parsing routines.
type ParseContext struct {
	DocumentName                        string
	TelepactSchemaDocumentsToPseudoJSON map[string][]any
	TelepactSchemaDocumentNamesToJSON   map[string]string
	SchemaKeysToDocumentName            map[string]string
	SchemaKeysToIndex                   map[string]int
	ParsedTypes                         map[string]types.TType
	FnErrorRegexes                      map[string]string
	AllParseFailures                    *[]*SchemaParseFailure
	FailedTypes                         map[string]struct{}
}

// Copy returns a shallow copy of the parse context with an optional document name override.
func (ctx *ParseContext) Copy(documentName string) *ParseContext {
	if ctx == nil {
		return nil
	}

	copy := *ctx
	if documentName != "" {
		copy.DocumentName = documentName
	}
	return &copy
}
