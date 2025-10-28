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
