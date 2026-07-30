//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// THeaders captures request/response header declarations for a function.
type THeaders struct {
	Name            string
	RequestHeaders  map[string]*TFieldDeclaration
	ResponseHeaders map[string]*TFieldDeclaration
}

// NewTHeaders constructs a THeaders instance.
func NewTHeaders(name string, requestHeaders, responseHeaders map[string]*TFieldDeclaration) *THeaders {
	return &THeaders{
		Name:            name,
		RequestHeaders:  requestHeaders,
		ResponseHeaders: responseHeaders,
	}
}
