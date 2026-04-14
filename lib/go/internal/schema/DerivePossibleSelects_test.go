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

package schema

import (
	"reflect"
	"testing"

	"github.com/telepact/telepact/lib/go/internal/types"
)

func TestDerivePossibleSelectsRecursiveResult(t *testing.T) {
	expression := types.NewTUnion("union.Expression", map[string]*types.TStruct{}, map[string]int{
		"Constant": 0,
		"Add":      1,
	})

	expression.Tags["Constant"] = types.NewTStruct("Constant", map[string]*types.TFieldDeclaration{
		"value": types.NewTFieldDeclaration("value", types.NewTTypeDeclaration(types.NewTNumber(), false, nil), false),
	})
	expression.Tags["Add"] = types.NewTStruct("Add", map[string]*types.TFieldDeclaration{
		"left":  types.NewTFieldDeclaration("left", types.NewTTypeDeclaration(expression, false, nil), false),
		"right": types.NewTFieldDeclaration("right", types.NewTTypeDeclaration(expression, false, nil), false),
	})

	evaluation := types.NewTStruct("struct.Evaluation", map[string]*types.TFieldDeclaration{
		"expression": types.NewTFieldDeclaration("expression", types.NewTTypeDeclaration(expression, false, nil), false),
		"result":     types.NewTFieldDeclaration("result", types.NewTTypeDeclaration(types.NewTNumber(), false, nil), false),
	})

	result := types.NewTUnion("fn.getPaperTape.->", map[string]*types.TStruct{
		"Ok_": types.NewTStruct("Ok_", map[string]*types.TFieldDeclaration{
			"tape": types.NewTFieldDeclaration("tape", types.NewTTypeDeclaration(types.NewTArray(), false, []*types.TTypeDeclaration{
				types.NewTTypeDeclaration(evaluation, false, nil),
			}), false),
		}),
	}, map[string]int{"Ok_": 0})

	actual := DerivePossibleSelects("fn.getPaperTape", result)
	expected := map[string]any{
		"->": map[string]any{
			"Ok_": []string{"tape"},
		},
		"struct.Evaluation": []string{"expression", "result"},
		"union.Expression": map[string][]string{
			"Add":      {"left", "right"},
			"Constant": {"value"},
		},
	}

	if !reflect.DeepEqual(actual, expected) {
		t.Fatalf("unexpected possible select: %#v", actual)
	}
}
