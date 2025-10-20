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

import "strings"

// ValidateHeaders validates request headers against parsed field declarations.
func ValidateHeaders(headers map[string]any, parsedRequestHeaders map[string]*TFieldDeclaration, functionName string) []*ValidationFailure {
	failures := make([]*ValidationFailure, 0)

	for header, value := range headers {
		if !strings.HasPrefix(header, "@") {
			failures = append(failures, NewValidationFailure([]any{header}, "RequiredObjectKeyPrefixMissing", map[string]any{"prefix": "@"}))
		}

		field := parsedRequestHeaders[header]
		if field == nil {
			continue
		}

		ctx := NewValidateContext(nil, functionName, false)
		nestedFailures := field.TypeDeclaration.Validate(value, ctx)
		failures = append(failures, prependPathToFailures(nestedFailures, header)...)
	}

	return failures
}
