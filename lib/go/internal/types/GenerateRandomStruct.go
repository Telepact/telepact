//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

import "sort"

// GenerateRandomStruct produces a pseudo-random struct object that respects the provided field declarations.
func GenerateRandomStruct(blueprintValue any, useBlueprintValue bool, referenceStruct map[string]*TFieldDeclaration, ctx *GenerateContext) map[string]any {
	if ctx == nil {
		return map[string]any{}
	}
	sortedKeys := make([]string, 0, len(referenceStruct))
	for key := range referenceStruct {
		sortedKeys = append(sortedKeys, key)
	}
	sort.Strings(sortedKeys)

	startingStruct := map[string]any{}
	if useBlueprintValue {
		startingStruct = toStringAnyMap(blueprintValue)
	}

	obj := make(map[string]any)
	for _, fieldName := range sortedKeys {
		fieldDeclaration := referenceStruct[fieldName]
		if fieldDeclaration == nil {
			continue
		}

		thisUseBlueprintValue := false
		var blueprintEntry any
		if useBlueprintValue {
			blueprintEntry, thisUseBlueprintValue = startingStruct[fieldName]
		}

		typeDeclaration := fieldDeclaration.TypeDeclaration

		if thisUseBlueprintValue {
			value := typeDeclaration.GenerateRandomValue(blueprintEntry, true, ctx)
			obj[fieldName] = value
			continue
		}

		if !fieldDeclaration.Optional {
			if !ctx.AlwaysIncludeRequiredFields && ctx.RandomGenerator != nil && ctx.RandomGenerator.NextBoolean() {
				continue
			}
			value := typeDeclaration.GenerateRandomValue(nil, false, ctx)
			obj[fieldName] = value
			continue
		}

		if !ctx.IncludeOptionalFields {
			continue
		}
		if ctx.RandomizeOptionalFields && ctx.RandomGenerator != nil && ctx.RandomGenerator.NextBoolean() {
			continue
		}

		value := typeDeclaration.GenerateRandomValue(nil, false, ctx)
		obj[fieldName] = value
	}

	return obj
}
