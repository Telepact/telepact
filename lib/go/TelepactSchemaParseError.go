//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package telepact

import (
	"fmt"

	"github.com/telepact/telepact/lib/go/internal/schema"
)

// TelepactSchemaParseError indicates a failure to parse a Telepact schema definition.
type TelepactSchemaParseError struct {
	SchemaParseFailures           []*schema.SchemaParseFailure
	SchemaParseFailuresPseudoJSON any
	message                       string
}

// NewTelepactSchemaParseError constructs a TelepactSchemaParseError with the supplied failures and schema documents.
func NewTelepactSchemaParseError(
	schemaParseFailures []*schema.SchemaParseFailure,
	telepactSchemaDocumentNamesToJSON map[string]string,
) *TelepactSchemaParseError {
	pseudoJSON := schema.MapSchemaParseFailuresToPseudoJSON(schemaParseFailures, telepactSchemaDocumentNamesToJSON)

	return &TelepactSchemaParseError{
		SchemaParseFailures:           schemaParseFailures,
		SchemaParseFailuresPseudoJSON: pseudoJSON,
		message:                       fmt.Sprintf("%v", pseudoJSON),
	}
}

// Error implements the error interface.
func (e *TelepactSchemaParseError) Error() string {
	if e == nil {
		return ""
	}
	return e.message
}
