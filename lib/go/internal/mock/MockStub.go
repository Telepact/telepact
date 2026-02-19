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

// MockStub represents a Telepact mock stub definition.
type MockStub struct {
	WhenFunction              string
	WhenArgument              map[string]any
	ThenResult                map[string]any
	AllowArgumentPartialMatch bool
	Count                     int
}

// NewMockStub constructs a MockStub using the supplied configuration.
func NewMockStub(
	whenFunction string,
	whenArgument map[string]any,
	thenResult map[string]any,
	allowArgumentPartialMatch bool,
	count int,
) *MockStub {
	return &MockStub{
		WhenFunction:              whenFunction,
		WhenArgument:              whenArgument,
		ThenResult:                thenResult,
		AllowArgumentPartialMatch: allowArgumentPartialMatch,
		Count:                     count,
	}
}
