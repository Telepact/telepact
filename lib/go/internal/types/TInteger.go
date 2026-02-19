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

const integerName = "Integer"

// TInteger represents the Telepact integer type.
type TInteger struct{}

// NewTInteger constructs a TInteger instance.
func NewTInteger() *TInteger {
	return &TInteger{}
}

// GetTypeParameterCount implements TType.
func (t *TInteger) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TInteger) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateInteger(value)
}

// GenerateRandomValue implements TType.
func (t *TInteger) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomInteger(blueprintValue, useBlueprintValue, ctx)
}

// GetName implements TType.
func (t *TInteger) GetName(ctx *ValidateContext) string {
	return integerName
}
