//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// ValidationFailure mirrors the Python structure capturing validation errors.
type ValidationFailure struct {
	Path   []any
	Reason string
	Data   map[string]any
}

// NewValidationFailure constructs a ValidationFailure using the supplied components.
func NewValidationFailure(path []any, reason string, data map[string]any) *ValidationFailure {
	return &ValidationFailure{
		Path:   append([]any{}, path...),
		Reason: reason,
		Data:   cloneStringInterfaceMap(data),
	}
}

func cloneStringInterfaceMap(source map[string]any) map[string]any {
	if source == nil {
		return map[string]any{}
	}
	clone := make(map[string]any, len(source))
	for key, value := range source {
		clone[key] = value
	}
	return clone
}
