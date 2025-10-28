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

const arrayName = "Array"

// TArray models an array type declaration.
type TArray struct{}

// NewTArray constructs a TArray instance.
func NewTArray() *TArray {
	return &TArray{}
}

// GetTypeParameterCount implements TType.
func (t *TArray) GetTypeParameterCount() int {
	return 1
}

// Validate implements TType.
func (t *TArray) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateArray(value, typeParameters, ctx)
}

// GenerateRandomValue implements TType.
func (t *TArray) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomArray(blueprintValue, useBlueprintValue, typeParameters, ctx)
}

// GetName implements TType.
func (t *TArray) GetName(ctx *ValidateContext) string {
	return arrayName
}
