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
