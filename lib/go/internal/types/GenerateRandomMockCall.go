//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

import (
	"sort"
	"strings"
)

// GenerateRandomMockCall produces a pseudo-random mock call structure based on the supplied schema types.
func GenerateRandomMockCall(typesMap map[string]TType, ctx *GenerateContext) any {
	if ctx == nil || ctx.RandomGenerator == nil {
		return nil
	}

	functionNames := make([]string, 0)
	for key := range typesMap {
		if strings.HasPrefix(key, "fn.") && !strings.HasSuffix(key, ".->") && !strings.HasSuffix(key, "_") {
			functionNames = append(functionNames, key)
		}
	}

	sort.Strings(functionNames)
	if len(functionNames) == 0 {
		return nil
	}

	selectedFnName := functionNames[ctx.RandomGenerator.NextIntWithCeiling(len(functionNames))]

	typeEntry := typesMap[selectedFnName]
	unionType, ok := typeEntry.(*TUnion)
	if !ok {
		return nil
	}

	alwaysIncludeRequired := false
	return GenerateRandomUnion(nil, false, unionType.Tags, ctx.Copy(nil, nil, &alwaysIncludeRequired, nil, nil))
}
