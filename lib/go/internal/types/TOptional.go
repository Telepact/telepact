//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const optionalName = "Optional"

// TOptional represents an optional Telepact type.
type TOptional struct {
	Type TType
}

// NewTOptional constructs a TOptional instance.
func NewTOptional(t TType) *TOptional {
	return &TOptional{Type: t}
}

// GetTypeParameterCount implements TType.
func (t *TOptional) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TOptional) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateOptional(value, t.Type, ctx)
}

// GenerateRandomValue implements TType.
func (t *TOptional) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	if useBlueprintValue {
		if blueprintValue == nil {
			return nil
		}
		return t.Type.GenerateRandomValue(blueprintValue, true, typeParameters, ctx)
	}

	if ctx != nil && ctx.RandomGenerator != nil {
		if ctx.RandomGenerator.NextBoolean() {
			return nil
		}
	}
	return t.Type.GenerateRandomValue(nil, false, typeParameters, ctx)
}

// GetName implements TType.
func (t *TOptional) GetName(ctx *ValidateContext) string {
	return optionalName
}
