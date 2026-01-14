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

const selectName = "Object"

// TSelect models a select type and holds the permissible selects map.
type TSelect struct {
	PossibleSelects map[string]any
}

// NewTSelect constructs a TSelect with the provided possible selects map.
func NewTSelect(possibleSelects map[string]any) *TSelect {
	return &TSelect{PossibleSelects: possibleSelects}
}

// GetTypeParameterCount implements TType.
func (t *TSelect) GetTypeParameterCount() int {
	return 0
}

// Validate implements TType by delegating to ValidateSelect.
func (t *TSelect) Validate(value any, typeParameters []*TTypeDeclaration, ctx *ValidateContext) []*ValidationFailure {
	return ValidateSelect(value, t.PossibleSelects, ctx)
}

// GenerateRandomValue implements TType.
func (t *TSelect) GenerateRandomValue(blueprintValue any, useBlueprintValue bool, typeParameters []*TTypeDeclaration, ctx *GenerateContext) any {
	return GenerateRandomSelect(t.PossibleSelects, ctx)
}

// GetName implements TType.
func (t *TSelect) GetName(ctx *ValidateContext) string {
	return selectName
}
