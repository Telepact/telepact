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

package telepact

import "encoding/binary"

var randomWords = []string{
	"alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
	"iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi",
	"rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega",
}

// RandomGenerator produces deterministic pseudo-random values used during mock generation.
type RandomGenerator struct {
	seed                int32
	collectionLengthMin int
	collectionLengthMax int
	count               int
}

// NewRandomGenerator constructs a RandomGenerator with the provided collection length bounds.
func NewRandomGenerator(collectionLengthMin, collectionLengthMax int) *RandomGenerator {
	rg := &RandomGenerator{
		collectionLengthMin: collectionLengthMin,
		collectionLengthMax: collectionLengthMax,
	}
	rg.SetSeed(0)
	return rg
}

// SetSeed sets the generator seed. A zero value is normalized to one to avoid the stationary state.
func (r *RandomGenerator) SetSeed(seed int32) {
	if seed == 0 {
		r.seed = 1
		return
	}
	r.seed = seed
}

// NextInt returns the next pseudo-random positive 31-bit integer.
func (r *RandomGenerator) NextInt() int {
	x := uint32(r.seed)
	x ^= x << 16
	x ^= x >> 11
	x ^= x << 5
	if x == 0 {
		x = 1
	}
	r.seed = int32(x)
	r.count++
	return int(int32(x & 0x7fffffff))
}

// NextIntWithCeiling returns the next pseudo-random integer modulo the provided ceiling.
func (r *RandomGenerator) NextIntWithCeiling(ceiling int) int {
	if ceiling == 0 {
		return 0
	}
	return r.NextInt() % ceiling
}

// NextBoolean returns a pseudo-random boolean value.
func (r *RandomGenerator) NextBoolean() bool {
	return r.NextIntWithCeiling(31) > 15
}

// NextBytes returns four pseudo-random bytes using big-endian encoding.
func (r *RandomGenerator) NextBytes() []byte {
	bytes := make([]byte, 4)
	binary.BigEndian.PutUint32(bytes, uint32(r.NextInt()))
	return bytes
}

// NextString returns a pseudo-random word from a deterministic dictionary.
func (r *RandomGenerator) NextString() string {
	index := r.NextIntWithCeiling(len(randomWords))
	return randomWords[index]
}

// NextDouble returns a pseudo-random floating-point value in the range [0, 1).
func (r *RandomGenerator) NextDouble() float64 {
	return float64(r.NextInt()&0x7fffffff) / float64(0x7fffffff)
}

// NextCollectionLength returns the next pseudo-random collection length within the configured bounds.
func (r *RandomGenerator) NextCollectionLength() int {
	offset := r.collectionLengthMax - r.collectionLengthMin
	if offset <= 0 {
		return r.collectionLengthMin
	}
	return r.NextIntWithCeiling(offset) + r.collectionLengthMin
}
