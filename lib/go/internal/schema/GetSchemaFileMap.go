//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import (
	"os"
	"path/filepath"
	"sort"
	"strings"
)

// GetSchemaFileMap reads Telepact schema resources beneath directory and returns their contents, along with any schema parse failures.
func GetSchemaFileMap(directory string) (map[string]string, []*SchemaParseFailure, error) {
	finalJSONDocuments := make(map[string]string)
	documentLocators := make(map[string]DocumentLocator)
	parseFailures := make([]*SchemaParseFailure, 0)

	entries, err := os.ReadDir(directory)
	if err != nil {
		return nil, nil, err
	}

	sort.Slice(entries, func(i, j int) bool {
		return entries[i].Name() < entries[j].Name()
	})

	for _, entry := range entries {
		relativePath := entry.Name()
		path := filepath.Join(directory, relativePath)

		if entry.IsDir() {
			parseFailures = append(parseFailures, NewSchemaParseFailure(relativePath, nil, "DirectoryDisallowed", map[string]any{}))
			finalJSONDocuments[relativePath] = "[]"
			continue
		}

		content, err := os.ReadFile(path)
		if err != nil {
			return nil, nil, err
		}

		switch {
		case strings.HasSuffix(relativePath, ".telepact.json"):
			finalJSONDocuments[relativePath] = string(content)
		case strings.HasSuffix(relativePath, ".telepact.yaml"):
			canonicalJSON, locator, err := ParseTelepactYAML(string(content))
			if err != nil {
				finalJSONDocuments[relativePath] = "[]"
				parseFailures = append(parseFailures, NewSchemaParseFailure(relativePath, nil, "JsonInvalid", map[string]any{}))
			} else {
				finalJSONDocuments[relativePath] = canonicalJSON
				documentLocators[relativePath] = locator
			}
		default:
			parseFailures = append(parseFailures, NewSchemaParseFailure(relativePath, nil, "FileNamePatternInvalid", map[string]any{"expected": "*.telepact.json|*.telepact.yaml"}))
			finalJSONDocuments[relativePath] = string(content)
		}
	}

	SetDocumentLocators(finalJSONDocuments, documentLocators)
	return finalJSONDocuments, parseFailures, nil
}
