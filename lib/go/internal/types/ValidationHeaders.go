//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
