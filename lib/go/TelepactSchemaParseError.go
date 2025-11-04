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
