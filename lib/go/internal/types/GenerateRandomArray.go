//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// GenerateRandomArray produces an array value compliant with the supplied type declaration.
func GenerateRandomArray(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) []any {
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
	if value == nil {
		return nil
	}

	if coerced, ok := coerceToInterfaceSlice(value); ok {
		return coerced
	}

	return nil
}
