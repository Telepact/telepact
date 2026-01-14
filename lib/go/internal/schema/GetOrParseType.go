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
	"strings"

	"github.com/telepact/telepact/lib/go/internal/types"
)

var typeNameRegex = regexp.MustCompile(`^(boolean|integer|number|string|any|bytes)|((fn|(union|struct|_ext))\.([a-zA-Z_]\w*))$`)

// GetOrParseType returns an existing parsed type or parses and stores it if necessary.
func GetOrParseType(path []any, typeName string, ctx *ParseContext) (types.TType, error) {
	if ctx == nil {
		return nil, nil
	}

	if ctx.FailedTypes != nil {
		if _, failed := ctx.FailedTypes[typeName]; failed {
			return nil, &ParseError{Failures: []*SchemaParseFailure{}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
		}
	}

	if ctx.ParsedTypes != nil {
		if existing, ok := ctx.ParsedTypes[typeName]; ok && existing != nil {
			return existing, nil
		}
	}

	matcher := typeNameRegex.FindStringSubmatch(typeName)
	if matcher == nil {
		failure := NewSchemaParseFailure(
			ctx.DocumentName,
			append([]any{}, path...),
			"StringRegexMatchFailed",
			map[string]any{"regex": typeNameRegex.String()},
		)
		return nil, &ParseError{Failures: []*SchemaParseFailure{failure}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	standardTypeName := matcher[1]
	if standardTypeName != "" {
		var typ types.TType
		switch standardTypeName {
		case "boolean":
			typ = types.NewTBoolean()
		case "integer":
			typ = types.NewTInteger()
		case "number":
			typ = types.NewTNumber()
		case "string":
			typ = types.NewTString()
		case "bytes":
			typ = types.NewTBytes()
		default:
			typ = types.NewTAny()
		}
		return storeParsedType(ctx, typeName, typ), nil
	}

	customTypeName := matcher[2]
	thisIndex, ok := ctx.SchemaKeysToIndex[customTypeName]
	if !ok {
		failure := NewSchemaParseFailure(
			ctx.DocumentName,
			append([]any{}, path...),
			"TypeUnknown",
			map[string]any{"name": customTypeName},
		)
		return nil, &ParseError{Failures: []*SchemaParseFailure{failure}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	thisDocumentName := ctx.SchemaKeysToDocumentName[customTypeName]
	documentDefinitions := ctx.TelepactSchemaDocumentsToPseudoJSON[thisDocumentName]
	if thisIndex < 0 || thisIndex >= len(documentDefinitions) {
		failure := NewSchemaParseFailure(
			ctx.DocumentName,
			append([]any{}, path...),
			"TypeDefinitionMissing",
			map[string]any{"name": customTypeName},
		)
		return nil, &ParseError{Failures: []*SchemaParseFailure{failure}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	definition, ok := documentDefinitions[thisIndex].(map[string]any)
	if !ok {
		failure := NewSchemaParseFailure(
			thisDocumentName,
			[]any{thisIndex},
			"TypeDefinitionUnexpected",
			map[string]any{"name": customTypeName},
		)
		return nil, &ParseError{Failures: []*SchemaParseFailure{failure}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	thisPath := []any{thisIndex}
	childCtx := ctx.Copy(thisDocumentName)

	var parsedType types.TType
	var err error

	switch {
	case strings.HasPrefix(customTypeName, "struct"):
		parsedType, err = ParseStructType(thisPath, definition, customTypeName, nil, childCtx)
	case strings.HasPrefix(customTypeName, "union"):
		parsedType, err = ParseUnionType(thisPath, definition, customTypeName, nil, nil, childCtx)
	case strings.HasPrefix(customTypeName, "fn"):
		argStruct, argErr := ParseStructType(path, definition, customTypeName, []string{"->", "_errors"}, ctx)
		if argErr != nil {
			err = argErr
			break
		}

		// Functions are represented as a single-variant union containing their call struct.
		unionTags := map[string]*types.TStruct{}
		unionIndices := map[string]int{}
		if argStruct != nil {
			unionTags[customTypeName] = argStruct
			unionIndices[customTypeName] = 0
		}
		storeParsedType(ctx, customTypeName, types.NewTUnion(customTypeName, unionTags, unionIndices))

		resultType, resultErr := ParseFunctionResultType(thisPath, definition, customTypeName, childCtx)
		if resultErr != nil {
			err = resultErr
			break
		}
		storeParsedType(ctx, customTypeName+".->", resultType)

		errorsRegex, regexErr := ParseFunctionErrorsRegex(thisPath, definition, customTypeName, childCtx)
		if regexErr != nil {
			err = regexErr
			break
		}
		if ctx.FnErrorRegexes != nil {
			ctx.FnErrorRegexes[customTypeName] = errorsRegex
		}
		return ctx.ParsedTypes[customTypeName], nil
	default:
		parsedType, err = resolveTypeExtension(customTypeName, path, ctx)
	}

	if err != nil {
		if parseErr, ok := err.(*ParseError); ok {
			if ctx.AllParseFailures != nil {
				*ctx.AllParseFailures = append(*ctx.AllParseFailures, parseErr.Failures...)
			}
			if ctx.FailedTypes == nil {
				ctx.FailedTypes = make(map[string]struct{})
			}
			ctx.FailedTypes[customTypeName] = struct{}{}
			return nil, &ParseError{Failures: []*SchemaParseFailure{}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
		}
		return nil, err
	}

	return storeParsedType(ctx, customTypeName, parsedType), nil
}

func storeParsedType(ctx *ParseContext, name string, typ types.TType) types.TType {
	if ctx.ParsedTypes == nil {
		ctx.ParsedTypes = make(map[string]types.TType)
	}
	if typ == nil {
		return nil
	}
	ctx.ParsedTypes[name] = typ
	return typ
}

func resolveTypeExtension(customTypeName string, path []any, ctx *ParseContext) (types.TType, error) {
	switch customTypeName {
	case "_ext.Select_":
		return types.NewTSelect(map[string]any{}), nil
	case "_ext.Call_":
		return types.NewTMockCall(ctx.ParsedTypes), nil
	case "_ext.Stub_":
		return types.NewTMockStub(ctx.ParsedTypes), nil
	default:
		failure := NewSchemaParseFailure(
			ctx.DocumentName,
			append([]any{}, path...),
			"TypeExtensionImplementationMissing",
			map[string]any{"name": customTypeName},
		)
		return nil, &ParseError{Failures: []*SchemaParseFailure{failure}, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}
}
