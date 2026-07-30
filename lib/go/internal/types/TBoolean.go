//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const booleanName = "Boolean"

// TBoolean represents the Telepact boolean type.
type TBoolean struct{}

// NewTBoolean constructs a TBoolean instance.
func NewTBoolean() *TBoolean {
	return &TBoolean{}
}

// GetTypeParameterCount implements TType.
func (t *TBoolean) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TBoolean) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateBoolean(value)
}

// GenerateRandomValue implements TType.
func (t *TBoolean) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomBoolean(blueprintValue, useBlueprintValue, ctx)
}

// GetName implements TType.
func (t *TBoolean) GetName(ctx *ValidateContext) string {
	return booleanName
}
