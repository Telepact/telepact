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

// GenerateRandomAny produces a pseudo-random primitive value.
func GenerateRandomAny(ctx *GenerateContext) any {
	if ctx == nil || ctx.RandomGenerator == nil {
		return nil
	}

	selectType := ctx.RandomGenerator.NextIntWithCeiling(3)
	switch selectType {
	case 0:
		return ctx.RandomGenerator.NextBoolean()
	case 1:
		return ctx.RandomGenerator.NextInt()
	default:
		return ctx.RandomGenerator.NextString()
	}
}
