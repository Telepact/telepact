//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const nullName = "Null"

// TNull represents the Telepact Null type.
type TNull struct{}

// NewTNull constructs a TNull instance.
func NewTNull() *TNull {
	return &TNull{}
}

// GetTypeParameterCount implements TType.
func (t *TNull) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TNull) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateNull(value, ctx)
}

// GenerateRandomValue implements TType.
func (t *TNull) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return nil
}

// GetName implements TType.
func (t *TNull) GetName(ctx *ValidateContext) string {
	return nullName
}
