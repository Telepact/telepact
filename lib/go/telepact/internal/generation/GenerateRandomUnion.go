//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package generation

import (
	"sort"

	"github.com/telepact/telepact/lib/go/telepact/internal/types"
)

// GenerateRandomUnion produces a pseudo-random union value respecting the supplied union tag definitions.
func GenerateRandomUnion(blueprintValue any, useBlueprintValue bool, unionTagsReference map[string]*types.TStruct, ctx *GenerateContext) map[string]any {
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
