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

// RandomGenerator captures the pseudo-random behaviour required during value generation.
type RandomGenerator interface {
	NextIntWithCeiling(int) int
	NextBoolean() bool
	NextInt() int
	NextString() string
	NextCollectionLength() int
	NextBytes() []byte
	NextDouble() float64
}

// GenerateContext carries contextual information used during mock value generation.
type GenerateContext struct {
	IncludeOptionalFields       bool
	RandomizeOptionalFields     bool
	AlwaysIncludeRequiredFields bool
	FnScope                     string
	RandomGenerator             RandomGenerator
}

// NewGenerateContext constructs a GenerateContext with the supplied values.
func NewGenerateContext(
	includeOptionalFields bool,
	randomizeOptionalFields bool,
	alwaysIncludeRequiredFields bool,
	fnScope string,
	randomGenerator RandomGenerator,
) *GenerateContext {
	return &GenerateContext{
		IncludeOptionalFields:       includeOptionalFields,
		RandomizeOptionalFields:     randomizeOptionalFields,
		AlwaysIncludeRequiredFields: alwaysIncludeRequiredFields,
		FnScope:                     fnScope,
		RandomGenerator:             randomGenerator,
	}
}

// Copy produces a new GenerateContext derived from the receiver, applying optional overrides where provided.
func (ctx *GenerateContext) Copy(
	includeOptionalFields *bool,
	randomizeOptionalFields *bool,
	alwaysIncludeRequiredFields *bool,
	fnScope *string,
	randomGenerator RandomGenerator,
) *GenerateContext {
	if ctx == nil {
		return nil
	}

	copy := *ctx

	if includeOptionalFields != nil {
		copy.IncludeOptionalFields = *includeOptionalFields
	}
	if randomizeOptionalFields != nil {
		copy.RandomizeOptionalFields = *randomizeOptionalFields
	}
	if alwaysIncludeRequiredFields != nil {
		copy.AlwaysIncludeRequiredFields = *alwaysIncludeRequiredFields
	}
	if fnScope != nil {
		copy.FnScope = *fnScope
	}
	if randomGenerator != nil {
		copy.RandomGenerator = randomGenerator
	}

	return &copy
}
