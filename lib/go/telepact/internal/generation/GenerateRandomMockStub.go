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
	"strings"

	"github.com/telepact/telepact/lib/go/telepact/internal/types"
)

// GenerateRandomMockStub creates a pseudo-random mock stub based on Telepact schema types.
func GenerateRandomMockStub(typesMap map[string]types.TType, ctx *GenerateContext) any {
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

	selectedFn, ok := typesMap[selectedFnName].(*types.TUnion)
	if !ok {
		return nil
	}

	selectedResult, ok := typesMap[selectedFnName+".->"].(*types.TUnion)
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
