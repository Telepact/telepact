//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const stringName = "String"

// TString represents the Telepact string type.
type TString struct{}

// NewTString constructs a TString instance.
func NewTString() *TString {
	return &TString{}
}

// GetTypeParameterCount implements TType.
func (t *TString) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TString) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateString(value)
}

// GenerateRandomValue implements TType.
func (t *TString) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomString(blueprintValue, useBlueprintValue, ctx)
}

// GetName implements TType.
func (t *TString) GetName(ctx *ValidateContext) string {
	return stringName
}
