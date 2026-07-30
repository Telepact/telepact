//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const numberName = "Number"

// TNumber represents the Telepact Number type.
type TNumber struct{}

// NewTNumber constructs a TNumber instance.
func NewTNumber() *TNumber {
	return &TNumber{}
}

// GetTypeParameterCount implements TType.
func (t *TNumber) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TNumber) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateNumber(value, ctx)
}

// GenerateRandomValue implements TType.
func (t *TNumber) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomNumber(blueprintValue, useBlueprintValue, ctx)
}

// GetName implements TType.
func (t *TNumber) GetName(ctx *ValidateContext) string {
	return numberName
}
