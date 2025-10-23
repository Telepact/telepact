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

import "github.com/telepact/telepact/lib/go/telepact/internal/types"

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
