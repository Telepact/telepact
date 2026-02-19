//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|
//|  you may not use this file except in compliance with the License.
//|
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package types

const numberName = "Number"

// TNumber represents the Telepact Number type.
type TNumber struct{}

// NewTNumber constructs a TNumber instance.
func NewTNumber() *TNumber {
	return &TNumber{}
}

// GetTypeParameterCount implements TType.
func (t *TNumber) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TNumber) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateNumber(value, ctx)
}

// GenerateRandomValue implements TType.
func (t *TNumber) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomNumber(blueprintValue, useBlueprintValue, ctx)
}

// GetName implements TType.
func (t *TNumber) GetName(ctx *ValidateContext) string {
	return numberName
}
