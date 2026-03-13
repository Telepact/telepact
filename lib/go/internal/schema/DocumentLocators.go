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
