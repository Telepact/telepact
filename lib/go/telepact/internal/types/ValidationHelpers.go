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

import "math"

// GetTypeUnexpectedValidationFailure mirrors the Python helper producing a standardized type mismatch failure.
func GetTypeUnexpectedValidationFailure(path []any, value any, expectedType string) []*ValidationFailure {
	data := map[string]any{
		"actual":   map[string]any{GetType(value): map[string]any{}},
		"expected": map[string]any{expectedType: map[string]any{}},
	}
	return []*ValidationFailure{NewValidationFailure(path, "TypeUnexpected", data)}
}

// prependPath prepends segments to an existing validation failure path.
func prependPath(failure *ValidationFailure, prefix ...any) *ValidationFailure {
	if failure == nil {
		return nil
	}
	newPath := make([]any, 0, len(prefix)+len(failure.Path))
	newPath = append(newPath, prefix...)
	newPath = append(newPath, failure.Path...)
	return &ValidationFailure{
		Path:   newPath,
		Reason: failure.Reason,
		Data:   cloneStringInterfaceMap(failure.Data),
	}
}

// prependPathToFailures applies prependPath to each failure in the slice.
func prependPathToFailures(failures []*ValidationFailure, prefix ...any) []*ValidationFailure {
	if len(failures) == 0 {
		return failures
	}
	result := make([]*ValidationFailure, 0, len(failures))
	for _, failure := range failures {
		result = append(result, prependPath(failure, prefix...))
	}
	return result
}

// withinSigned64Bit checks whether v fits within signed 64-bit range.
func withinSigned64Bit(v float64) bool {
	return v <= math.MaxInt64 && v >= math.MinInt64
}
