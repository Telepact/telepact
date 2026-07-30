//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

import (
	"sort"
	"strings"
)

// GenerateRandomMockStub creates a pseudo-random mock stub based on Telepact schema types.
func GenerateRandomMockStub(typesMap map[string]TType, ctx *GenerateContext) any {
	if ctx == nil || ctx.RandomGenerator == nil {
		return nil
	}

	functions := make([]string, 0)
	for key := range typesMap {
		if strings.HasPrefix(key, "fn.") && !strings.HasSuffix(key, ".->") && !strings.HasSuffix(key, "_") {
			functions = append(functions, key)
		}
	}

	sort.Strings(functions)
	if len(functions) == 0 {
		return nil
	}

	index := ctx.RandomGenerator.NextIntWithCeiling(len(functions))
	selectedFnName := functions[index]

	selectedFn, ok := typesMap[selectedFnName].(*TUnion)
	if !ok {
		return nil
	}

	selectedResult, ok := typesMap[selectedFnName+".->"].(*TUnion)
	if !ok {
		return nil
	}

	argFields := selectedFn.Tags[selectedFnName].Fields
	okFields := selectedResult.Tags["Ok_"].Fields

	alwaysIncludeRequired := false
	arg := GenerateRandomStruct(nil, false, argFields, ctx.Copy(nil, nil, &alwaysIncludeRequired, nil, nil))
	okResult := GenerateRandomStruct(nil, false, okFields, ctx.Copy(nil, nil, &alwaysIncludeRequired, nil, nil))

	return map[string]any{
		selectedFnName: arg,
		"->": map[string]any{
			"Ok_": okResult,
		},
	}
}
