//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// TTypeDeclaration encapsulates a type reference along with nullability and nested type parameters.
type TTypeDeclaration struct {
	Type           TType
	Nullable       bool
	TypeParameters []*TTypeDeclaration
}

// NewTTypeDeclaration constructs a TTypeDeclaration mirroring the Python constructor.
func NewTTypeDeclaration(t TType, nullable bool, typeParameters []*TTypeDeclaration) *TTypeDeclaration {
	return &TTypeDeclaration{
		Type:           t,
		Nullable:       nullable,
		TypeParameters: typeParameters,
	}
}

// Validate ensures the given value conforms to the declaration's type rules.
func (d *TTypeDeclaration) Validate(value any, ctx *ValidateContext) []*ValidationFailure {
	if d == nil || d.Type == nil {
		return nil
	}
	return ValidateValueOfType(value, d.Type, d.Nullable, d.TypeParameters, ctx)
}

// GenerateRandomValue produces a pseudo-random value that conforms to the declaration.
func (d *TTypeDeclaration) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, ctx *GenerateContext) any {
	if d == nil || d.Type == nil {
		return nil
	}
	return GenerateRandomValueOfType(blueprintValue, useBlueprintValue, d.Type, d.Nullable, d.TypeParameters, ctx)
}
