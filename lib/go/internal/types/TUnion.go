//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const unionName = "Object"

// TUnion represents a union type definition in Telepact.
type TUnion struct {
	Name       string
	Tags       map[string]*TStruct
	TagIndices map[string]int
}

// NewTUnion constructs a TUnion instance.
func NewTUnion(name string, tags map[string]*TStruct, tagIndices map[string]int) *TUnion {
	return &TUnion{Name: name, Tags: tags, TagIndices: tagIndices}
}

// GetTypeParameterCount implements TType.
func (t *TUnion) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TUnion) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateUnion(value, t.Name, t.Tags, ctx)
}

// GenerateRandomValue implements TType.
func (t *TUnion) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomUnion(blueprintValue, useBlueprintValue, t.Tags, ctx)
}

// GetName implements TType.
func (t *TUnion) GetName(ctx *ValidateContext) string {
	return unionName
}
