//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
