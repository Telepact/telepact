//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const mockStubName = "_ext.Stub_"

// TMockStub represents an external mock stub type.
type TMockStub struct {
	Types map[string]TType
}

// NewTMockStub constructs a TMockStub instance.
func NewTMockStub(types map[string]TType) *TMockStub {
	return &TMockStub{Types: types}
}

// GetTypeParameterCount implements TType.
func (t *TMockStub) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TMockStub) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateMockStub(value, t.Types, ctx)
}

// GenerateRandomValue implements TType.
func (t *TMockStub) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomMockStub(t.Types, ctx)
}

// GetName implements TType.
func (t *TMockStub) GetName(ctx *ValidateContext) string {
	return mockStubName
}
