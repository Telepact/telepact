//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const anyName = "Any"

// TAny represents Telepact's wildcard type.
type TAny struct{}

// NewTAny constructs a TAny instance.
func NewTAny() *TAny {
	return &TAny{}
}

// GetTypeParameterCount implements TType.
func (t *TAny) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType by accepting all values.
func (t *TAny) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return nil
}

// GenerateRandomValue implements TType by delegating to GenerateRandomAny.
func (t *TAny) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomAny(ctx)
}

// GetName implements TType.
func (t *TAny) GetName(ctx *ValidateContext) string {
	return anyName
}
