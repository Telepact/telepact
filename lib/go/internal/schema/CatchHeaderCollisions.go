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

import "sort"

// CatchHeaderCollisions reports duplicate header definitions across Telepact schema documents.
func CatchHeaderCollisions(
	telepactSchemaNameToPseudoJSON map[string][]any,
	headerKeys map[string]struct{},
	keysToIndex map[string]int,
	schemaKeysToDocumentNames map[string]string,
	documentNamesToJSON map[string]string,
) ([]*SchemaParseFailure, error) {
	if len(headerKeys) == 0 {
		return nil, nil
	}

	headers := make([]string, 0, len(headerKeys))
	for key := range headerKeys {
		headers = append(headers, key)
	}

	sort.Slice(headers, func(i, j int) bool {
		docI := schemaKeysToDocumentNames[headers[i]]
		docJ := schemaKeysToDocumentNames[headers[j]]
		if docI == docJ {
			return keysToIndex[headers[i]] < keysToIndex[headers[j]]
		}
		return docI < docJ
	})

	parseFailures := make([]*SchemaParseFailure, 0)

	for i := 0; i < len(headers); i++ {
		for j := i + 1; j < len(headers); j++ {
			defKey := headers[i]
			otherDefKey := headers[j]

			index := keysToIndex[defKey]
			otherIndex := keysToIndex[otherDefKey]

			documentName := schemaKeysToDocumentNames[defKey]
			otherDocumentName := schemaKeysToDocumentNames[otherDefKey]

			pseudoList := telepactSchemaNameToPseudoJSON[documentName]
			otherPseudoList := telepactSchemaNameToPseudoJSON[otherDocumentName]
			if index < 0 || index >= len(pseudoList) || otherIndex < 0 || otherIndex >= len(otherPseudoList) {
				continue
			}

			defMap, ok := pseudoList[index].(map[string]any)
			if !ok {
				continue
			}
			otherDefMap, ok := otherPseudoList[otherIndex].(map[string]any)
			if !ok {
				continue
			}

			headerDef, ok := defMap[defKey].(map[string]any)
			if !ok {
				continue
			}
			otherHeaderDef, ok := otherDefMap[otherDefKey].(map[string]any)
			if !ok {
				continue
			}

			headerCollisions := intersectKeys(headerDef, otherHeaderDef)
			for _, collision := range headerCollisions {
				thisPath := []any{index, defKey, collision}
				thisDocJSON := documentNamesToJSON[documentName]
				location := GetPathDocumentCoordinatesPseudoJSON(thisPath, thisDocJSON)
				parseFailures = append(parseFailures, NewSchemaParseFailure(
					otherDocumentName,
					[]any{otherIndex, otherDefKey, collision},
					"PathCollision",
					map[string]any{
						"document": documentName,
						"path":     thisPath,
						"location": location,
					},
				))
			}

			resHeaderDef, ok := defMap["->"].(map[string]any)
			if !ok {
				continue
			}
			otherResHeaderDef, ok := otherDefMap["->"].(map[string]any)
			if !ok {
				continue
			}

			resCollisions := intersectKeys(resHeaderDef, otherResHeaderDef)
			for _, collision := range resCollisions {
				thisPath := []any{index, "->", collision}
				thisDocJSON := documentNamesToJSON[documentName]
				location := GetPathDocumentCoordinatesPseudoJSON(thisPath, thisDocJSON)
				parseFailures = append(parseFailures, NewSchemaParseFailure(
					otherDocumentName,
					[]any{otherIndex, "->", collision},
					"PathCollision",
					map[string]any{
						"document": documentName,
						"path":     thisPath,
						"location": location,
					},
				))
			}
		}
	}

	return parseFailures, nil
}

func intersectKeys(a, b map[string]any) []string {
	result := make([]string, 0)
	for key := range a {
		if _, exists := b[key]; exists {
			result = append(result, key)
		}
	}
	return result
}
