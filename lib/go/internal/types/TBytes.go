//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const bytesName = "Bytes"

// TBytes represents the Telepact bytes type.
type TBytes struct{}

// NewTBytes constructs a TBytes instance.
func NewTBytes() *TBytes {
	return &TBytes{}
}

// GetTypeParameterCount implements TType.
func (t *TBytes) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TBytes) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateBytes(value, ctx)
}

// GenerateRandomValue implements TType.
func (t *TBytes) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomBytes(blueprintValue, useBlueprintValue, ctx)
}

// GetName implements TType.
func (t *TBytes) GetName(ctx *ValidateContext) string {
	return bytesName
}
