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

import (
	"regexp"

	"github.com/telepact/telepact/lib/go/internal/types"
)

// ParseField parses a single struct or header field declaration.
func ParseField(path []any, fieldDeclaration string, typeDeclarationValue any, isHeader bool, ctx *ParseContext) (*types.TFieldDeclaration, error) {
	if ctx == nil {
		return nil, nil
	}

	headerRegex := "^@[a-z][a-zA-Z0-9_]*$"
	fieldRegex := "^([a-z][a-zA-Z0-9_]*)(!)?$"

	regexToUse := fieldRegex
	if isHeader {
		regexToUse = headerRegex
	}

	regex := regexp.MustCompile(regexToUse)
	matches := regex.FindStringSubmatch(fieldDeclaration)
	if matches == nil {
		failurePath := append(append([]any{}, path...), fieldDeclaration)
		failure := NewSchemaParseFailure(ctx.DocumentName, failurePath, "KeyRegexMatchFailed", map[string]any{"regex": regexToUse})
		return nil, &ParseError{Failures: []*SchemaParseFailure{failure}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	fieldName := fieldDeclaration
	optional := true
	if !isHeader {
		fieldName = matches[0]
		optional = matches[2] != ""
	}

	typePath := append(append([]any{}, path...), fieldName)
	typeDeclaration, err := ParseTypeDeclaration(typePath, typeDeclarationValue, ctx)
	if err != nil {
		return nil, err
	}

	return types.NewTFieldDeclaration(fieldName, typeDeclaration, optional), nil
}
