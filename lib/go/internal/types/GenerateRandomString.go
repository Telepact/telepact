//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// GenerateRandomString returns a pseudo-random string, optionally reusing a blueprint value.
func GenerateRandomString(blueprintValue any, useBlueprintValue bool, ctx *GenerateContext) any {
	if useBlueprintValue {
		return blueprintValue
	}
	if ctx == nil || ctx.RandomGenerator == nil {
		return ""
	}
	return ctx.RandomGenerator.NextString()
}
