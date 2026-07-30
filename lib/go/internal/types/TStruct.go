//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

const structName = "Object"

// TStruct represents a struct type definition in Telepact.
type TStruct struct {
	Name   string
	Fields map[string]*TFieldDeclaration
}

// NewTStruct constructs a TStruct instance.
func NewTStruct(name string, fields map[string]*TFieldDeclaration) *TStruct {
	return &TStruct{Name: name, Fields: fields}
}

// GetTypeParameterCount implements TType.
func (t *TStruct) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TStruct) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateStruct(value, t.Name, t.Fields, ctx)
}

// GenerateRandomValue implements TType.
func (t *TStruct) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomStruct(blueprintValue, useBlueprintValue, t.Fields, ctx)
}

// GetName implements TType.
func (t *TStruct) GetName(ctx *ValidateContext) string {
	return structName
}
