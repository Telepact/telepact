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
	"github.com/telepact/telepact/lib/go/internal/schema"
	"github.com/telepact/telepact/lib/go/internal/types"
)

// TelepactSchema represents a parsed Telepact schema.
type TelepactSchema struct {
	Original              []any
	Parsed                map[string]types.TType
	ParsedRequestHeaders  map[string]*types.TFieldDeclaration
	ParsedResponseHeaders map[string]*types.TFieldDeclaration
}

// NewTelepactSchema constructs a TelepactSchema with the supplied values.
func NewTelepactSchema(
	original []any,
	parsed map[string]types.TType,
	parsedRequestHeaders map[string]*types.TFieldDeclaration,
	parsedResponseHeaders map[string]*types.TFieldDeclaration,
) *TelepactSchema {
	return &TelepactSchema{
		Original:              cloneAnySlice(original),
		Parsed:                parsed,
		ParsedRequestHeaders:  parsedRequestHeaders,
		ParsedResponseHeaders: parsedResponseHeaders,
	}
}

// TelepactSchemaFromJSON constructs a TelepactSchema from JSON content.
func TelepactSchemaFromJSON(json string) (*TelepactSchema, error) {
	result, err := schema.CreateTelepactSchemaFromFileJSONMap(map[string]string{"auto_": json})
	if err != nil {
		return nil, wrapParseError(err)
	}
	return telepactSchemaFromParsed(result), nil
}

// TelepactSchemaFromFileJSONMap constructs a TelepactSchema from a map of filenames to JSON content.
func TelepactSchemaFromFileJSONMap(fileJSONMap map[string]string) (*TelepactSchema, error) {
	result, err := schema.CreateTelepactSchemaFromFileJSONMap(fileJSONMap)
	if err != nil {
		return nil, wrapParseError(err)
	}
	return telepactSchemaFromParsed(result), nil
}

// TelepactSchemaFromDirectory constructs a TelepactSchema from the JSON files contained in a directory.
func TelepactSchemaFromDirectory(directory string) (*TelepactSchema, error) {
	schemaFileMap, parseFailures, err := schema.GetSchemaFileMap(directory)
	if err != nil {
		return nil, err
	}
	if len(parseFailures) > 0 {
		return nil, NewTelepactSchemaParseError(parseFailures, schemaFileMap)
	}
	result, err := schema.CreateTelepactSchemaFromFileJSONMap(schemaFileMap)
	if err != nil {
		return nil, wrapParseError(err)
	}
	return telepactSchemaFromParsed(result), nil
}

// ParsedDefinitions returns the parsed schema definitions keyed by message name.
func (t *TelepactSchema) ParsedDefinitions() map[string]types.TType {
	if t == nil {
		return nil
	}
	return t.Parsed
}

// RequestHeaderDeclarations returns the parsed request header declarations keyed by header name.
func (t *TelepactSchema) RequestHeaderDeclarations() map[string]*types.TFieldDeclaration {
	if t == nil {
		return nil
	}
	return t.ParsedRequestHeaders
}

// ResponseHeaderDeclarations returns the parsed response header declarations keyed by header name.
func (t *TelepactSchema) ResponseHeaderDeclarations() map[string]*types.TFieldDeclaration {
	if t == nil {
		return nil
	}
	return t.ParsedResponseHeaders
}

// OriginalDefinitions returns the original schema definitions slice.
func (t *TelepactSchema) OriginalDefinitions() []any {
	if t == nil {
		return nil
	}
	return t.Original
}

func telepactSchemaFromParsed(result *schema.ParsedSchemaResult) *TelepactSchema {
	if result == nil {
		return nil
	}
	return NewTelepactSchema(result.Original, result.Parsed, result.ParsedRequestHeaders, result.ParsedResponseHeaders)
}

func wrapParseError(err error) error {
	if err == nil {
		return nil
	}
	if parseErr, ok := err.(*schema.ParseError); ok {
		return NewTelepactSchemaParseError(parseErr.Failures, parseErr.DocumentJSON)
	}
	return err
}
