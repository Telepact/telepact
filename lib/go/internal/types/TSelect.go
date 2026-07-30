//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const selectName = "Object"

// TSelect models a select type and holds the permissible selects map.
type TSelect struct {
	PossibleSelects map[string]any
}

// NewTSelect constructs a TSelect with the provided possible selects map.
func NewTSelect(possibleSelects map[string]any) *TSelect {
	return &TSelect{PossibleSelects: possibleSelects}
}

// GetTypeParameterCount implements TType.
func (t *TSelect) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType by delegating to ValidateSelect.
func (t *TSelect) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateSelect(value, t.PossibleSelects, ctx)
}

// GenerateRandomValue implements TType.
func (t *TSelect) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomSelect(t.PossibleSelects, ctx)
}

// GetName implements TType.
func (t *TSelect) GetName(ctx *ValidateContext) string {
	return selectName
}
