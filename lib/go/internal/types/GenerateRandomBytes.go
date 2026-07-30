//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// GenerateRandomBytes returns a pseudo-random byte slice, optionally reusing a blueprint value.
func GenerateRandomBytes(blueprintValue any, useBlueprintValue bool, ctx *GenerateContext) any {
	if useBlueprintValue {
		return blueprintValue
	}
	if ctx == nil || ctx.RandomGenerator == nil {
		return nil
	}
	return ctx.RandomGenerator.NextBytes()
}
