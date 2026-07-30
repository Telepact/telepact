//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

import "sort"

// GenerateRandomUnion produces a pseudo-random union value respecting the supplied union tag definitions.
func GenerateRandomUnion(blueprintValue any, useBlueprintValue bool, unionTagsReference map[string]*TStruct, ctx *GenerateContext) map[string]any {
	if ctx == nil {
		return map[string]any{}
	}

	if !useBlueprintValue {
		sortedUnionTags := make([]string, 0, len(unionTagsReference))
		for key := range unionTagsReference {
			sortedUnionTags = append(sortedUnionTags, key)
		}
		sort.Strings(sortedUnionTags)

		if len(sortedUnionTags) == 0 {
			return map[string]any{}
		}

		randomIndex := 0
		if ctx.RandomGenerator != nil {
			randomIndex = ctx.RandomGenerator.NextIntWithCeiling(len(sortedUnionTags))
		}

		unionTag := sortedUnionTags[randomIndex]
		unionStruct := unionTagsReference[unionTag]
		structValue := GenerateRandomStruct(nil, false, unionStruct.Fields, ctx)
		return map[string]any{unionTag: structValue}
	}

	startingUnion := toStringAnyMap(blueprintValue)
	for unionTag, unionValue := range startingUnion {
		unionStruct := unionTagsReference[unionTag]
		startingStruct := toStringAnyMap(unionValue)
		structValue := GenerateRandomStruct(startingStruct, true, unionStruct.Fields, ctx)
		return map[string]any{unionTag: structValue}
	}

	return map[string]any{}
}
