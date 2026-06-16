//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import (
	"regexp"
	"sort"
)

// FindSchemaKey identifies the canonical schema key for a definition within a document.
func FindSchemaKey(documentName string, definition map[string]any, index int, documentNamesToJSON map[string]string) (string, error) {
	regex := regexp.MustCompile(`^(((fn|errors|headers|info)|((struct|union|_ext)(<[0-2]>)?))\..*)`)
	matches := make([]string, 0)

	keys := make([]string, 0, len(definition))
	for key := range definition {
		keys = append(keys, key)
	}
	sort.Strings(keys)

	for _, key := range keys {
		if regex.MatchString(key) {
			matches = append(matches, key)
		}
	}

	if len(matches) == 1 {
		return matches[0], nil
	}

	failure := NewSchemaParseFailure(
		documentName,
		[]any{index},
		"ObjectKeyRegexMatchCountUnexpected",
		map[string]any{
			"regex":    regex.String(),
			"actual":   len(matches),
			"expected": 1,
			"keys":     keys,
		},
	)

	return "", &ParseError{
		Failures:     []*SchemaParseFailure{failure},
		DocumentJSON: documentNamesToJSON,
	}
}
