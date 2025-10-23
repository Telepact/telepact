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

// CatchErrorCollisions detects duplicate error paths across definitions and returns parse failures when collisions are found.
func CatchErrorCollisions(
	telepactSchemaNameToPseudoJSON map[string][]any,
	errorKeys map[string]struct{},
	keysToIndex map[string]int,
	schemaKeysToDocumentName map[string]string,
	documentNamesToJSON map[string]string,
) ([]*SchemaParseFailure, error) {
	if len(errorKeys) == 0 {
		return nil, nil
	}

	keys := make([]string, 0, len(errorKeys))
	for key := range errorKeys {
		keys = append(keys, key)
	}

	sort.Slice(keys, func(i, j int) bool {
		docI := schemaKeysToDocumentName[keys[i]]
		docJ := schemaKeysToDocumentName[keys[j]]
		if docI == docJ {
			return keysToIndex[keys[i]] < keysToIndex[keys[j]]
		}
		return docI < docJ
	})

	parseFailures := make([]*SchemaParseFailure, 0)

	for i := 0; i < len(keys); i++ {
		for j := i + 1; j < len(keys); j++ {
			defKey := keys[i]
			otherDefKey := keys[j]

			index := keysToIndex[defKey]
			otherIndex := keysToIndex[otherDefKey]

			documentName := schemaKeysToDocumentName[defKey]
			otherDocumentName := schemaKeysToDocumentName[otherDefKey]

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

			errDefList, ok := toAnySlice(defMap[defKey])
			if !ok {
				continue
			}
			otherErrDefList, ok := toAnySlice(otherDefMap[otherDefKey])
			if !ok {
				continue
			}

			for k := 0; k < len(errDefList); k++ {
				thisErrDef, ok := errDefList[k].(map[string]any)
				if !ok {
					continue
				}
				thisKeys := keySetWithoutMeta(thisErrDef)
				if len(thisKeys) == 0 {
					continue
				}

				for l := 0; l < len(otherErrDefList); l++ {
					otherErrDef, ok := otherErrDefList[l].(map[string]any)
					if !ok {
						continue
					}
					otherKeys := keySetWithoutMeta(otherErrDef)
					if len(otherKeys) == 0 {
						continue
					}

					if keySetsEqual(thisKeys, otherKeys) {
						thisErrorKey := firstKey(thisKeys)
						otherErrorKey := firstKey(otherKeys)

						finalPath := []any{index, defKey, k, thisErrorKey}
						otherPath := []any{otherIndex, otherDefKey, l, otherErrorKey}

						otherDocumentJSON := documentNamesToJSON[documentName]
						otherLocation := GetPathDocumentCoordinatesPseudoJSON(finalPath, otherDocumentJSON)

						parseFailures = append(parseFailures, NewSchemaParseFailure(
							otherDocumentName,
							otherPath,
							"PathCollision",
							map[string]any{
								"document": documentName,
								"path":     finalPath,
								"location": otherLocation,
							},
						))
					}
				}
			}
		}
	}

	return parseFailures, nil
}

func toAnySlice(value any) ([]any, bool) {
	switch v := value.(type) {
	case []any:
		return v, true
	default:
		return nil, false
	}
}

func keySetWithoutMeta(m map[string]any) map[string]struct{} {
	result := make(map[string]struct{}, len(m))
	for key := range m {
		if key == "///" {
			continue
		}
		result[key] = struct{}{}
	}
	return result
}

func keySetsEqual(a, b map[string]struct{}) bool {
	if len(a) != len(b) {
		return false
	}
	for key := range a {
		if _, ok := b[key]; !ok {
			return false
		}
	}
	return true
}

func firstKey(m map[string]struct{}) string {
	for key := range m {
		return key
	}
	return ""
}
