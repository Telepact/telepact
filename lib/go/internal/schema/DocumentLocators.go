//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

import (
	"reflect"
	"sync"
)

type DocumentLocator func(path []any) map[string]any

var documentLocatorRegistry sync.Map

func mapIdentity(documentNamesToJSON map[string]string) uintptr {
	return reflect.ValueOf(documentNamesToJSON).Pointer()
}

func SetDocumentLocators(documentNamesToJSON map[string]string, documentLocators map[string]DocumentLocator) {
	if documentNamesToJSON == nil {
		return
	}

	cloned := make(map[string]DocumentLocator, len(documentLocators))
	for key, value := range documentLocators {
		cloned[key] = value
	}
	documentLocatorRegistry.Store(mapIdentity(documentNamesToJSON), cloned)
}

func CopyDocumentLocators(src map[string]string, dst map[string]string) {
	if src == nil || dst == nil {
		return
	}

	value, ok := documentLocatorRegistry.Load(mapIdentity(src))
	if !ok {
		return
	}

	locators, ok := value.(map[string]DocumentLocator)
	if !ok {
		return
	}

	SetDocumentLocators(dst, locators)
}

func ResolveDocumentCoordinates(path []any, documentName string, documentNamesToJSON map[string]string) map[string]any {
	if value, ok := documentLocatorRegistry.Load(mapIdentity(documentNamesToJSON)); ok {
		if locators, ok := value.(map[string]DocumentLocator); ok {
			if locator, ok := locators[documentName]; ok && locator != nil {
				return locator(append([]any{}, path...))
			}
		}
	}

	return GetPathDocumentCoordinatesPseudoJSON(append([]any{}, path...), documentNamesToJSON[documentName])
}
