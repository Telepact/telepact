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

const optionalName = "Optional"

// TOptional represents an optional Telepact type.
type TOptional struct {
	Type TType
}

// NewTOptional constructs a TOptional instance.
func NewTOptional(t TType) *TOptional {
	return &TOptional{Type: t}
}

// GetTypeParameterCount implements TType.
func (t *TOptional) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType.
func (t *TOptional) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateOptional(value, t.Type, ctx)
}

// GenerateRandomValue implements TType.
func (t *TOptional) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	if useBlueprintValue {
		if blueprintValue == nil {
			return nil
		}
		return t.Type.GenerateRandomValue(blueprintValue, true, typeParameters, ctx)
	}

	if ctx != nil && ctx.RandomGenerator != nil {
		if ctx.RandomGenerator.NextBoolean() {
			return nil
		}
	}
	return t.Type.GenerateRandomValue(nil, false, typeParameters, ctx)
}

// GetName implements TType.
func (t *TOptional) GetName(ctx *ValidateContext) string {
	return optionalName
}
