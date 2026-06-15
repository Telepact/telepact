//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package schema

// ParseError represents a collection of schema parse failures.
type ParseError struct {
	Failures     []*SchemaParseFailure
	DocumentJSON map[string]string
}

// Error implements the error interface.
func (e *ParseError) Error() string {
	if e == nil {
		return ""
	}
	return "telepact: schema parse failure"
}
