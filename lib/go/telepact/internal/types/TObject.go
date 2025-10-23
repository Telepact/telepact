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

const objectName = "Object"

// TObject represents the Telepact Object type.
type TObject struct{}

// NewTObject constructs a TObject instance.
func NewTObject() *TObject {
	return &TObject{}
}

// GetTypeParameterCount implements TType.
func (t *TObject) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TObject) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateObject(value, typeParameters, ctx)
}

// GenerateRandomValue implements TType.
func (t *TObject) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomObject(blueprintValue, useBlueprintValue, typeParameters, ctx)
}

// GetName implements TType.
func (t *TObject) GetName(ctx *ValidateContext) string {
	return objectName
}
