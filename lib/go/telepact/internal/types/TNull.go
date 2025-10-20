//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
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

const nullName = "Null"

// TNull represents the Telepact Null type.
type TNull struct{}

// NewTNull constructs a TNull instance.
func NewTNull() *TNull {
	return &TNull{}
}

// GetTypeParameterCount implements TType.
func (t *TNull) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TNull) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateNull(value, ctx)
}

// GenerateRandomValue implements TType.
func (t *TNull) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return nil
}

// GetName implements TType.
func (t *TNull) GetName(ctx *ValidateContext) string {
	return nullName
}
