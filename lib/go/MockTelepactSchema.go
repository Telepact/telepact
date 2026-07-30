//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package telepact

import (
	"github.com/telepact/telepact/lib/go/internal/schema"
	"github.com/telepact/telepact/lib/go/internal/types"
)

// MockTelepactSchema represents a schema prepared for mock usage.
type MockTelepactSchema struct {
	Original              []any
	Full                  []any
	Parsed                map[string]types.TType
	ParsedRequestHeaders  map[string]*types.TFieldDeclaration
	ParsedResponseHeaders map[string]*types.TFieldDeclaration
}

// NewMockTelepactSchema constructs a MockTelepactSchema with the supplied values.
func NewMockTelepactSchema(
	original []any,
	full []any,
	parsed map[string]types.TType,
	parsedRequestHeaders map[string]*types.TFieldDeclaration,
	parsedResponseHeaders map[string]*types.TFieldDeclaration,
) *MockTelepactSchema {
	return &MockTelepactSchema{
		Original:              cloneAnySlice(original),
		Full:                  cloneAnySlice(full),
		Parsed:                parsed,
		ParsedRequestHeaders:  parsedRequestHeaders,
		ParsedResponseHeaders: parsedResponseHeaders,
	}
}

// MockTelepactSchemaFromJSON constructs a MockTelepactSchema from JSON content.
func MockTelepactSchemaFromJSON(json string) (*MockTelepactSchema, error) {
	result, err := schema.CreateMockTelepactSchemaFromFileJSONMap(map[string]string{"auto_": json})
	if err != nil {
		return nil, wrapParseError(err)
	}
	return mockTelepactSchemaFromParsed(result), nil
}

// MockTelepactSchemaFromFileJSONMap constructs a MockTelepactSchema from a map of filenames to JSON content.
func MockTelepactSchemaFromFileJSONMap(fileJSONMap map[string]string) (*MockTelepactSchema, error) {
	result, err := schema.CreateMockTelepactSchemaFromFileJSONMap(fileJSONMap)
	if err != nil {
		return nil, wrapParseError(err)
	}
	return mockTelepactSchemaFromParsed(result), nil
}

// MockTelepactSchemaFromDirectory constructs a MockTelepactSchema from the JSON files contained in a directory.
func MockTelepactSchemaFromDirectory(directory string) (*MockTelepactSchema, error) {
	schemaFileMap, parseFailures, err := schema.GetSchemaFileMap(directory)
	if err != nil {
		return nil, err
	}
	if len(parseFailures) > 0 {
		return nil, NewTelepactSchemaParseError(parseFailures, schemaFileMap)
	}
	result, err := schema.CreateMockTelepactSchemaFromFileJSONMap(schemaFileMap)
	if err != nil {
		return nil, wrapParseError(err)
	}
	return mockTelepactSchemaFromParsed(result), nil
}

// ParsedDefinitions returns the parsed schema definitions keyed by message name.
func (m *MockTelepactSchema) ParsedDefinitions() map[string]types.TType {
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

// FullDefinitions returns the complete schema definitions slice, including Telepact internals.
func (m *MockTelepactSchema) FullDefinitions() []any {
	if m == nil {
		return nil
	}
	return m.Full
}

func cloneAnySlice(values []any) []any {
	if values == nil {
		return nil
	}
	cloned := make([]any, len(values))
	copy(cloned, values)
	return cloned
}

func mockTelepactSchemaFromParsed(result *schema.ParsedSchemaResult) *MockTelepactSchema {
	if result == nil {
		return nil
	}
	return NewMockTelepactSchema(result.Original, result.Full, result.Parsed, result.ParsedRequestHeaders, result.ParsedResponseHeaders)
}
