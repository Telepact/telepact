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

package generation

import (
	"sort"

	"github.com/telepact/telepact/lib/go/telepact/internal/types"
)

// GenerateRandomStruct produces a pseudo-random struct object that respects the provided field declarations.
func GenerateRandomStruct(blueprintValue any, useBlueprintValue bool, referenceStruct map[string]*types.TFieldDeclaration, ctx *GenerateContext) map[string]any {
	if ctx == nil {
		return map[string]any{}
	}
	sortedKeys := make([]string, 0, len(referenceStruct))
	for key := range referenceStruct {
		sortedKeys = append(sortedKeys, key)
	}
	sort.Strings(sortedKeys)

	startingStruct := map[string]any{}
	if useBlueprintValue {
		startingStruct = toStringAnyMap(blueprintValue)
	}

	obj := make(map[string]any)
	for _, fieldName := range sortedKeys {
		fieldDeclaration := referenceStruct[fieldName]
		if fieldDeclaration == nil {
			continue
		}

		thisUseBlueprintValue := false
		var blueprintEntry any
		if useBlueprintValue {
			blueprintEntry, thisUseBlueprintValue = startingStruct[fieldName]
		}

		typeDeclaration := fieldDeclaration.TypeDeclaration

		if thisUseBlueprintValue {
			value := typeDeclaration.GenerateRandomValue(blueprintEntry, true, ctx)
			obj[fieldName] = value
			continue
		}

		if !fieldDeclaration.Optional {
			if !ctx.AlwaysIncludeRequiredFields && ctx.RandomGenerator != nil && ctx.RandomGenerator.NextBoolean() {
				continue
			}
			value := typeDeclaration.GenerateRandomValue(nil, false, ctx)
			obj[fieldName] = value
			continue
		}

		if !ctx.IncludeOptionalFields {
			continue
		}
		if ctx.RandomizeOptionalFields && ctx.RandomGenerator != nil && ctx.RandomGenerator.NextBoolean() {
			continue
		}

		value := typeDeclaration.GenerateRandomValue(nil, false, ctx)
		obj[fieldName] = value
	}

	return obj
}
