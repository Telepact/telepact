//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
