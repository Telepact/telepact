//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|
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
