//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const mockCallName = "_ext.Call_"

// TMockCall represents an external mock call type.
type TMockCall struct {
	Types map[string]TType
}

// NewTMockCall constructs a TMockCall instance.
func NewTMockCall(types map[string]TType) *TMockCall {
	return &TMockCall{Types: types}
}

// GetTypeParameterCount implements TType.
func (t *TMockCall) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TMockCall) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateMockCall(value, t.Types, ctx)
}

// GenerateRandomValue implements TType.
func (t *TMockCall) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomMockCall(t.Types, ctx)
}

// GetName implements TType.
func (t *TMockCall) GetName(ctx *ValidateContext) string {
	return mockCallName
}
