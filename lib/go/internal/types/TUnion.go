//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
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
