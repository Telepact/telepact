//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package mock

// MockInvocation captures an invocation observed by the Telepact mock server implementation.
type MockInvocation struct {
	FunctionName     string
	FunctionArgument map[string]any
	Verified         bool
}

// NewMockInvocation constructs a MockInvocation with the supplied function name and argument.
func NewMockInvocation(functionName string, functionArgument map[string]any) *MockInvocation {
	return &MockInvocation{
		FunctionName:     functionName,
		FunctionArgument: functionArgument,
		Verified:         false,
	}
}
