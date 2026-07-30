//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// toStringAnyMap normalises arbitrary map representations into map[string]any, returning an empty map when coercion fails.
func toStringAnyMap(value any) map[string]any {
	if value == nil {
		return map[string]any{}
	}

	if coerced, ok := coerceToStringAnyMap(value); ok {
		return coerced
	}

	return map[string]any{}
}
