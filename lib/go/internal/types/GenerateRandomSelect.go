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

package types

import (
	"fmt"
	"sort"
)

// GenerateRandomSelect builds a pseudo-random select projection using the provided context.
func GenerateRandomSelect(possibleSelects map[string]any, ctx *GenerateContext) any {
	if ctx == nil {
		return nil
	}

	possibleSelect := possibleSelects[ctx.FnScope]
	return subSelect(possibleSelect, ctx)
}

func subSelect(possibleSelectSection any, ctx *GenerateContext) any {
	switch typed := possibleSelectSection.(type) {
	case []any:
		selectedFieldNames := make([]string, 0)
		for _, entry := range typed {
			fieldName, ok := entry.(string)
			if !ok {
				continue
			}

			if ctx.RandomGenerator == nil || ctx.RandomGenerator.NextBoolean() {
				selectedFieldNames = append(selectedFieldNames, fieldName)
			}
		}
		sort.Strings(selectedFieldNames)
		return selectedFieldNames
	case []string:
		selectedFieldNames := make([]string, 0, len(typed))
		for _, fieldName := range typed {
			if ctx.RandomGenerator == nil || ctx.RandomGenerator.NextBoolean() {
				selectedFieldNames = append(selectedFieldNames, fieldName)
			}
		}
		sort.Strings(selectedFieldNames)
		return selectedFieldNames
	case map[string]any:
		selectedSection := make(map[string]any)
		keys := make([]string, 0, len(typed))
		for key := range typed {
			keys = append(keys, key)
		}
		sort.Strings(keys)

		for _, key := range keys {
			value := typed[key]
			if ctx.RandomGenerator != nil && !ctx.RandomGenerator.NextBoolean() {
				continue
			}

			result := subSelect(value, ctx)
			if nestedMap, ok := result.(map[string]any); ok && len(nestedMap) == 0 {
				continue
			}
			selectedSection[key] = result
		}

		return selectedSection
	case map[string][]string:
		converted := make(map[string]any, len(typed))
		for key, value := range typed {
			converted[key] = value
		}
		return subSelect(converted, ctx)
	case map[any]any:
		converted := make(map[string]any, len(typed))
		for key, value := range typed {
			converted[fmt.Sprintf("%v", key)] = value
		}
		return subSelect(converted, ctx)
	default:
		panic(fmt.Errorf("invalid possible_select_section: %T", possibleSelectSection))
	}
}
