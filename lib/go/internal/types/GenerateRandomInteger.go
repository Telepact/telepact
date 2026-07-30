//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// GenerateRandomInteger returns a pseudo-random integer, optionally reusing a blueprint value.
func GenerateRandomInteger(blueprintValue any, useBlueprintValue bool, ctx *GenerateContext) any {
	if useBlueprintValue {
		return blueprintValue
	}
	if ctx == nil || ctx.RandomGenerator == nil {
		return 0
	}
	return ctx.RandomGenerator.NextInt()
}
