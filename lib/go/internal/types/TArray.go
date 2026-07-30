//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const arrayName = "Array"

// TArray models an array type declaration.
type TArray struct{}

// NewTArray constructs a TArray instance.
func NewTArray() *TArray {
	return &TArray{}
}

// GetTypeParameterCount implements TType.
func (t *TArray) GetTypeParameterCount() int {
	return 1
}

// Validate implements TType.
func (t *TArray) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateArray(value, typeParameters, ctx)
}

// GenerateRandomValue implements TType.
func (t *TArray) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomArray(blueprintValue, useBlueprintValue, typeParameters, ctx)
}

// GetName implements TType.
func (t *TArray) GetName(ctx *ValidateContext) string {
	return arrayName
}
