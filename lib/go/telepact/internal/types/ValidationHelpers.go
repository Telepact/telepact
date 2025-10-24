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
	"math"
	"sort"
	"strings"
)

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

func sortValidationFailures(failures []*ValidationFailure) {
	sort.SliceStable(failures, func(i, j int) bool {
		cmp := comparePaths(failures[i].Path, failures[j].Path)
		if cmp != 0 {
			return cmp < 0
		}
		return failures[i].Reason < failures[j].Reason
	})
}

func comparePaths(a, b []any) int {
	if len(a) == 0 && len(b) == 0 {
		return 0
	}
	if len(a) == 0 {
		return -1
	}
	if len(b) == 0 {
		return 1
	}
	limit := len(a)
	if len(b) < limit {
		limit = len(b)
	}
	for i := 0; i < limit; i++ {
		segA := segmentSortableString(a[i])
		segB := segmentSortableString(b[i])
		if cmp := strings.Compare(segA, segB); cmp != 0 {
			return cmp
		}
	}
	if len(a) < len(b) {
		return -1
	}
	if len(a) > len(b) {
		return 1
	}
	return 0
}

func segmentSortableString(value any) string {
	switch v := value.(type) {
	case string:
		return "0:" + v
	case int:
		return fmt.Sprintf("1:%020d", v)
	case int64:
		return fmt.Sprintf("1:%020d", v)
	case float64:
		return fmt.Sprintf("2:%f", v)
	default:
		return fmt.Sprintf("3:%v", v)
	}
}

// withinSigned64Bit checks whether v fits within signed 64-bit range.
func withinSigned64Bit(v float64) bool {
	return v <= math.MaxInt64 && v >= math.MinInt64
}
