//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const objectName = "Object"

// TObject represents the Telepact Object type.
type TObject struct{}

// NewTObject constructs a TObject instance.
func NewTObject() *TObject {
	return &TObject{}
}

// GetTypeParameterCount implements TType.
func (t *TObject) GetTypeParameterCount() int {
	return 1
}

// Validate implements TType.
func (t *TObject) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateObject(value, typeParameters, ctx)
}

// GenerateRandomValue implements TType.
func (t *TObject) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomObject(blueprintValue, useBlueprintValue, typeParameters, ctx)
}

// GetName implements TType.
func (t *TObject) GetName(ctx *ValidateContext) string {
	return objectName
}
