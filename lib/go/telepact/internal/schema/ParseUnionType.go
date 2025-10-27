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
	"sort"

	"github.com/telepact/telepact/lib/go/telepact/internal/types"
)

// ParseUnionType parses a union type definition from pseudo JSON.
func ParseUnionType(path []any, unionDefinition map[string]any, schemaKey string, ignoreKeys []string, requiredKeys []string, ctx *ParseContext) (*types.TUnion, error) {
	if ctx == nil {
		return nil, nil
	}

	parseFailures := make([]*SchemaParseFailure, 0)

	otherKeys := make(map[string]struct{}, len(unionDefinition))
	for key := range unionDefinition {
		otherKeys[key] = struct{}{}
	}

	delete(otherKeys, schemaKey)
	delete(otherKeys, "///")
	for _, key := range ignoreKeys {
		delete(otherKeys, key)
	}

	for key := range otherKeys {
		failurePath := append(append([]any{}, path...), key)
		parseFailures = append(parseFailures, NewSchemaParseFailure(ctx.DocumentName, failurePath, "ObjectKeyDisallowed", map[string]any{}))
	}

	thisPath := append(append([]any{}, path...), schemaKey)
	defInit, ok := unionDefinition[schemaKey]
	if !ok {
		defInit = nil
	}

	defSlice, ok := defInit.([]any)
	if !ok {
		parseFailures = append(parseFailures, GetTypeUnexpectedParseFailure(ctx.DocumentName, thisPath, defInit, "Array")...)
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	definition := make([]map[string]any, 0, len(defSlice))
	for index, element := range defSlice {
		loopPath := append(append([]any{}, thisPath...), index)
		elementMap, ok := element.(map[string]any)
		if !ok {
			parseFailures = append(parseFailures, GetTypeUnexpectedParseFailure(ctx.DocumentName, loopPath, element, "Object")...)
			continue
		}
		definition = append(definition, elementMap)
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	if len(definition) == 0 {
		parseFailures = append(parseFailures, NewSchemaParseFailure(ctx.DocumentName, thisPath, "EmptyArrayDisallowed", map[string]any{}))
	} else {
		for _, requiredKey := range requiredKeys {
			found := false
			for _, element := range definition {
				tagKeys := make(map[string]struct{}, len(element))
				for key := range element {
					if key == "///" {
						continue
					}
					tagKeys[key] = struct{}{}
				}
				if _, ok := tagKeys[requiredKey]; ok {
					found = true
					break
				}
			}
			if !found {
				branchPath := append(append([]any{}, thisPath...), 0)
				parseFailures = append(parseFailures, NewSchemaParseFailure(ctx.DocumentName, branchPath, "RequiredObjectKeyMissing", map[string]any{"key": requiredKey}))
			}
		}
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	tags := make(map[string]*types.TStruct, len(definition))
	tagIndices := make(map[string]int, len(definition))
	regex := regexp.MustCompile(`^([A-Z][a-zA-Z0-9_]*)$`)

	for index, element := range definition {
		loopPath := append(append([]any{}, thisPath...), index)
		elementCopy := make(map[string]any, len(element))
		for k, v := range element {
			if k == "///" {
				continue
			}
			elementCopy[k] = v
		}

		keys := make([]string, 0, len(elementCopy))
		for key := range elementCopy {
			keys = append(keys, key)
		}
		sort.Strings(keys)

		matches := make([]string, 0)
		for _, key := range keys {
			if regex.MatchString(key) {
				matches = append(matches, key)
			}
		}

		if len(matches) != 1 {
			parseFailures = append(parseFailures, NewSchemaParseFailure(ctx.DocumentName, loopPath, "ObjectKeyRegexMatchCountUnexpected", map[string]any{
				"regex":    regex.String(),
				"actual":   len(matches),
				"expected": 1,
				"keys":     keys,
			}))
			continue
		}

		if len(elementCopy) != 1 {
			parseFailures = append(parseFailures, NewSchemaParseFailure(ctx.DocumentName, loopPath, "ObjectSizeUnexpected", map[string]any{
				"expected": 1,
				"actual":   len(elementCopy),
			}))
			continue
		}

		unionTag := matches[0]
		entryValue := elementCopy[unionTag]
		unionKeyPath := append(append([]any{}, loopPath...), unionTag)

		unionTagStruct, ok := entryValue.(map[string]any)
		if !ok {
			parseFailures = append(parseFailures, GetTypeUnexpectedParseFailure(ctx.DocumentName, unionKeyPath, entryValue, "Object")...)
			continue
		}

		fields, err := ParseStructFields(unionKeyPath, unionTagStruct, false, ctx)
		if err != nil {
			if parseErr, ok := err.(*ParseError); ok {
				parseFailures = append(parseFailures, parseErr.Failures...)
			} else {
				return nil, err
			}
			continue
		}

		tags[unionTag] = types.NewTStruct(schemaKey+"."+unionTag, fields)
		tagIndices[unionTag] = index
	}

	if len(parseFailures) > 0 {
		return nil, &ParseError{Failures: parseFailures, DocumentJSON: ctx.TelepactSchemaDocumentNamesToJSON}
	}

	return types.NewTUnion(schemaKey, tags, tagIndices), nil
}
