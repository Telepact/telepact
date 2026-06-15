//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

func CreatePathDocumentYAMLCoordinatesPseudoJSONLocator(text string) (DocumentLocator, error) {
	return createDocumentLocatorFromYAMLText(text)
}

func GetPathDocumentYAMLCoordinatesPseudoJSON(path []any, document string) (location map[string]any) {
	locator, err := CreatePathDocumentYAMLCoordinatesPseudoJSONLocator(document)
	if err != nil {
		return defaultDocumentCoordinates()
	}
	return locator(path)
}
