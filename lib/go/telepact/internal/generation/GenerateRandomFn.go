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

package generation

import "github.com/telepact/telepact/lib/go/telepact/internal/types"

// GenerateRandomFn delegates to GenerateRandomUnion for function unions.
func GenerateRandomFn(blueprintValue any, useBlueprintValue bool, callTags map[string]*types.TStruct, ctx *GenerateContext) any {
	return GenerateRandomUnion(blueprintValue, useBlueprintValue, callTags, ctx)
}
