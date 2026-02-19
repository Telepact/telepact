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

package types

// GenerateRandomObject produces a pseudo-random object adhering to the provided type declaration.
func GenerateRandomObject(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) map[string]any {
	if len(typeParameters) == 0 {
		return map[string]any{}
	}

	nestedTypeDeclaration := typeParameters[0]

	if useBlueprintValue {
		startingObj, _ := coerceToStringAnyMap(blueprintValue)
		obj := make(map[string]any, len(startingObj))
		for key, startingValue := range startingObj {
			value := nestedTypeDeclaration.GenerateRandomValue(startingValue, true, ctx)
			obj[key] = value
		}
		return obj
	}

	length := 0
	if ctx != nil && ctx.RandomGenerator != nil {
		length = ctx.RandomGenerator.NextCollectionLength()
	}

	obj := make(map[string]any, length)
	for i := 0; i < length; i++ {
		key := ""
		if ctx != nil && ctx.RandomGenerator != nil {
			key = ctx.RandomGenerator.NextString()
		}
		value := nestedTypeDeclaration.GenerateRandomValue(nil, false, ctx)
		obj[key] = value
	}

	return obj
}
