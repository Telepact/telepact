//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
