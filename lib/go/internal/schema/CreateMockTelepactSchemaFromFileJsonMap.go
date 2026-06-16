//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

// CreateMockTelepactSchemaFromFileJSONMap constructs a mock Telepact schema from the supplied JSON documents map.
func CreateMockTelepactSchemaFromFileJSONMap(jsonDocuments map[string]string) (*ParsedSchemaResult, error) {
	finalDocuments := make(map[string]string, len(jsonDocuments)+1)
	for key, value := range jsonDocuments {
		finalDocuments[key] = value
	}
	CopyDocumentLocators(jsonDocuments, finalDocuments)

	finalDocuments["mock_"] = GetMockTelepactJSON()

	return CreateTelepactSchemaFromFileJSONMap(finalDocuments)
}
