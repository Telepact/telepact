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
	"encoding/json"
	"regexp"
)

// CreateTelepactSchemaFromFileJSONMap constructs a Telepact schema from the supplied JSON documents map.
func CreateTelepactSchemaFromFileJSONMap(jsonDocuments map[string]string) (*ParsedSchemaResult, error) {
	finalDocuments := make(map[string]string, len(jsonDocuments)+1)
	for key, value := range jsonDocuments {
		finalDocuments[key] = value
	}
	CopyDocumentLocators(jsonDocuments, finalDocuments)

	internalJSON := GetInternalTelepactJSON()
	if !hasBundledDefinitions(jsonDocuments, "internal_", internalJSON) {
		finalDocuments["internal_"] = internalJSON
	}

	authPattern := regexp.MustCompile(`"union\.Auth_"\s*:`)
	authJSON := GetAuthTelepactJSON()
	for _, document := range jsonDocuments {
		if authPattern.MatchString(document) {
			if !hasBundledDefinitions(jsonDocuments, "auth_", authJSON) {
				finalDocuments["auth_"] = authJSON
			}
			break
		}
	}

	return ParseTelepactSchema(finalDocuments)
}

func hasBundledDefinitions(jsonDocuments map[string]string, bundledDocumentName, bundledJSON string) bool {
	bundledKeys, ok := collectSchemaKeys(map[string]string{bundledDocumentName: bundledJSON})
	if !ok {
		return false
	}

	providedKeys, ok := collectSchemaKeys(jsonDocuments)
	if !ok {
		return false
	}

	for key := range bundledKeys {
		if _, ok := providedKeys[key]; !ok {
			return false
		}
	}
	return true
}

func collectSchemaKeys(jsonDocuments map[string]string) (map[string]struct{}, bool) {
	schemaKeys := make(map[string]struct{})

	for documentName, documentJSON := range jsonDocuments {
		var pseudoJSON []any
		if err := json.Unmarshal([]byte(documentJSON), &pseudoJSON); err != nil {
			return nil, false
		}

		for index, definitionRaw := range pseudoJSON {
			definition, ok := definitionRaw.(map[string]any)
			if !ok {
				continue
			}

			schemaKey, err := FindSchemaKey(documentName, definition, index, jsonDocuments)
			if err != nil {
				return nil, false
			}
			schemaKeys[schemaKey] = struct{}{}
		}
	}

	return schemaKeys, true
}
