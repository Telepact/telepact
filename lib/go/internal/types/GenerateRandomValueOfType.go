//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// GenerateRandomValueOfType produces a pseudo-random value for the provided type declaration.
func GenerateRandomValueOfType(
	blueprintValue any,
	useBlueprintValue bool,
	thisType TType,
	nullable bool,
	typeParameters []*TTypeDeclaration,
	ctx *GenerateContext,
) any {
	if nullable && !useBlueprintValue && ctx != nil && ctx.RandomGenerator != nil && ctx.RandomGenerator.NextBoolean() {
		return nil
	}

	return thisType.GenerateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx)
}
