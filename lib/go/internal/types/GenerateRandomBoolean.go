//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// GenerateRandomBoolean returns a pseudo-random boolean, optionally reusing a blueprint value.
func GenerateRandomBoolean(blueprintValue any, useBlueprintValue bool, ctx *GenerateContext) any {
	if useBlueprintValue {
		return blueprintValue
	}
	if ctx == nil || ctx.RandomGenerator == nil {
		return nil
	}
	return ctx.RandomGenerator.NextBoolean()
}
