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
	"github.com/telepact/telepact/lib/go/telepact/internal/schema"
	"github.com/telepact/telepact/lib/go/telepact/internal/types"
)

// MockTelepactSchema represents a schema prepared for mock usage.
type MockTelepactSchema struct {
	Original              []any
	Parsed                map[string]*types.TType
	ParsedRequestHeaders  map[string]*types.TFieldDeclaration
	ParsedResponseHeaders map[string]*types.TFieldDeclaration
}

// NewMockTelepactSchema constructs a MockTelepactSchema with the supplied values.
func NewMockTelepactSchema(
	original []any,
	parsed map[string]*types.TType,
	parsedRequestHeaders map[string]*types.TFieldDeclaration,
	parsedResponseHeaders map[string]*types.TFieldDeclaration,
) *MockTelepactSchema {
	return &MockTelepactSchema{
		Original:              cloneAnySlice(original),
		Parsed:                parsed,
		ParsedRequestHeaders:  parsedRequestHeaders,
		ParsedResponseHeaders: parsedResponseHeaders,
	}
}

// MockTelepactSchemaFromJSON constructs a MockTelepactSchema from JSON content.
func MockTelepactSchemaFromJSON(json string) (*MockTelepactSchema, error) {
	return schema.CreateMockTelepactSchemaFromFileJSONMap(map[string]string{"auto_": json})
}

// MockTelepactSchemaFromFileJSONMap constructs a MockTelepactSchema from a map of filenames to JSON content.
func MockTelepactSchemaFromFileJSONMap(fileJSONMap map[string]string) (*MockTelepactSchema, error) {
	return schema.CreateMockTelepactSchemaFromFileJSONMap(fileJSONMap)
}

// MockTelepactSchemaFromDirectory constructs a MockTelepactSchema from the JSON files contained in a directory.
func MockTelepactSchemaFromDirectory(directory string) (*MockTelepactSchema, error) {
	schemaFileMap, err := schema.GetSchemaFileMap(directory)
	if err != nil {
		return nil, err
	}
	return schema.CreateMockTelepactSchemaFromFileJSONMap(schemaFileMap)
}

// ParsedDefinitions returns the parsed schema definitions keyed by message name.
func (m *MockTelepactSchema) ParsedDefinitions() map[string]*types.TType {
	if m == nil {
		return nil
	}
	return m.Parsed
}

// RequestHeaderDeclarations returns the parsed request header declarations keyed by header name.
func (m *MockTelepactSchema) RequestHeaderDeclarations() map[string]*types.TFieldDeclaration {
	if m == nil {
		return nil
	}
	return m.ParsedRequestHeaders
}

// ResponseHeaderDeclarations returns the parsed response header declarations keyed by header name.
func (m *MockTelepactSchema) ResponseHeaderDeclarations() map[string]*types.TFieldDeclaration {
	if m == nil {
		return nil
	}
	return m.ParsedResponseHeaders
}

// OriginalDefinitions returns the original schema definitions slice.
func (m *MockTelepactSchema) OriginalDefinitions() []any {
	if m == nil {
		return nil
	}
	return m.Original
}

func cloneAnySlice(values []any) []any {
	if values == nil {
		return nil
	}
	cloned := make([]any, len(values))
	copy(cloned, values)
	return cloned
}
