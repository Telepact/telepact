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
