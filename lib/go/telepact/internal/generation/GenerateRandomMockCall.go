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

// GenerateRandomMockCall produces a pseudo-random mock call structure based on the supplied schema types.
func GenerateRandomMockCall(typesMap map[string]types.TType, ctx *GenerateContext) any {
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
	unionType, ok := typeEntry.(*types.TUnion)
	if !ok {
		return nil
	}

	alwaysIncludeRequired := false
	return GenerateRandomUnion(nil, false, unionType.Tags, ctx.Copy(nil, nil, &alwaysIncludeRequired, nil, nil))
}
