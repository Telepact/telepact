//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// MapValidationFailuresToInvalidFieldCases mirrors the Python helper for serialising validation failures.
func MapValidationFailuresToInvalidFieldCases(argumentValidationFailures []*ValidationFailure) []map[string]any {
	cases := make([]map[string]any, 0, len(argumentValidationFailures))
	for _, failure := range argumentValidationFailures {
		if failure == nil {
			continue
		}
		cases = append(cases, map[string]any{
			"path":   append([]any{}, failure.Path...),
			"reason": map[string]any{failure.Reason: cloneStringInterfaceMap(failure.Data)},
		})
	}
	return cases
}
