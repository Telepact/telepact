//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

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
