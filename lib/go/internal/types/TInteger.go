//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const integerName = "Integer"

// TInteger represents the Telepact integer type.
type TInteger struct{}

// NewTInteger constructs a TInteger instance.
func NewTInteger() *TInteger {
	return &TInteger{}
}

// GetTypeParameterCount implements TType.
func (t *TInteger) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TInteger) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateInteger(value)
}

// GenerateRandomValue implements TType.
func (t *TInteger) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomInteger(blueprintValue, useBlueprintValue, ctx)
}

// GetName implements TType.
func (t *TInteger) GetName(ctx *ValidateContext) string {
	return integerName
}
