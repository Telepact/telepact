//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

func GetPathDocumentCoordinatesPseudoJSON(path []any, document string) map[string]any {
	locator, err := createDocumentLocatorFromYAMLText(document)
	if err != nil {
		return defaultDocumentCoordinates()
	}
	return locator(append([]any{}, path...))
}
