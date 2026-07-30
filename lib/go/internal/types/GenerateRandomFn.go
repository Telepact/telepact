//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// GenerateRandomFn delegates to GenerateRandomUnion for function unions.
func GenerateRandomFn(blueprintValue any, useBlueprintValue bool, callTags map[string]*TStruct, ctx *GenerateContext) any {
	return GenerateRandomUnion(blueprintValue, useBlueprintValue, callTags, ctx)
}
