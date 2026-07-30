//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// GenerateRandomNumber returns a pseudo-random floating-point number, optionally reusing a blueprint value.
func GenerateRandomNumber(blueprintValue any, useBlueprintValue bool, ctx *GenerateContext) any {
	if useBlueprintValue {
		return blueprintValue
	}
	if ctx == nil || ctx.RandomGenerator == nil {
		return 0.0
	}
	return ctx.RandomGenerator.NextDouble()
}
