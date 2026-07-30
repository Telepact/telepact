//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// TType represents a Telepact schema type node.
type TType interface {
	GetTypeParameterCount() int
	Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure
	GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any
	GetName(ctx *ValidateContext) string
}
