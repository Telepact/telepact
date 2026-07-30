//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// GenerateRandomAny produces a pseudo-random primitive value.
func GenerateRandomAny(ctx *GenerateContext) any {
	if ctx == nil || ctx.RandomGenerator == nil {
		return nil
	}

	selectType := ctx.RandomGenerator.NextIntWithCeiling(3)
	switch selectType {
	case 0:
		return ctx.RandomGenerator.NextBoolean()
	case 1:
		return ctx.RandomGenerator.NextInt()
	default:
		return ctx.RandomGenerator.NextString()
	}
}
