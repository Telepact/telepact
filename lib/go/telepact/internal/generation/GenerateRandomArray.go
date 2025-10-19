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

import "github.com/telepact/telepact/lib/go/telepact/internal/types"

// GenerateRandomArray produces an array value compliant with the supplied type declaration.
func GenerateRandomArray(blueprintValue any, useBlueprintValue bool, typeParameters []*types.TTypeDeclaration, ctx *GenerateContext) []any {
	if len(typeParameters) == 0 {
		return []any{}
	}

	nestedTypeDeclaration := typeParameters[0]

	if useBlueprintValue {
		startingArray := toAnySlice(blueprintValue)
		array := make([]any, 0, len(startingArray))
		for _, startingValue := range startingArray {
			value := nestedTypeDeclaration.GenerateRandomValue(startingValue, true, ctx)
			array = append(array, value)
		}
		return array
	}

	length := 0
	if ctx != nil && ctx.RandomGenerator != nil {
		length = ctx.RandomGenerator.NextCollectionLength()
	}

	array := make([]any, 0, length)
	for i := 0; i < length; i++ {
		value := nestedTypeDeclaration.GenerateRandomValue(nil, false, ctx)
		array = append(array, value)
	}

	return array
}

func toAnySlice(value any) []any {
	switch typed := value.(type) {
	case []any:
		return typed
	default:
		return []any{}
	}
}
