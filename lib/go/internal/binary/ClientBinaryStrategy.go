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

package binary

import (
	"sync"
	"time"
)

type checksumRecord struct {
	value      int
	expiration int
}

// ClientBinaryStrategy tracks checksum rotation for client binary encoding.
type ClientBinaryStrategy struct {
	cache      BinaryEncodingCache
	primary    *checksumRecord
	secondary  *checksumRecord
	lastUpdate time.Time
	mu         sync.Mutex
}

// NewClientBinaryStrategy constructs a ClientBinaryStrategy instance.
func NewClientBinaryStrategy(cache BinaryEncodingCache) *ClientBinaryStrategy {
	return &ClientBinaryStrategy{
		cache:      cache,
		lastUpdate: time.Now(),
	}
}

// UpdateChecksum records a newly observed checksum, rotating the primary/secondary slots when necessary.
func (s *ClientBinaryStrategy) UpdateChecksum(newChecksum int) {
	s.mu.Lock()
	defer s.mu.Unlock()

	now := time.Now()

	if s.primary == nil {
		s.primary = &checksumRecord{value: newChecksum}
		s.lastUpdate = now
		return
	}

	if s.primary.value != newChecksum {
		expired := s.secondary
		s.secondary = s.primary
		s.primary = &checksumRecord{value: newChecksum}
		if s.secondary != nil {
			s.secondary.expiration++
		}
		if expired != nil {
			s.cache.Remove(expired.value)
		}
		s.lastUpdate = now
		return
	}

	s.lastUpdate = now
}

// GetCurrentChecksums returns the current checksum order, retiring the secondary checksum after inactivity.
func (s *ClientBinaryStrategy) GetCurrentChecksums() []int {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.primary == nil {
		return []int{}
	}

	if s.secondary == nil {
		return []int{s.primary.value}
	}

	minutesSinceUpdate := time.Since(s.lastUpdate).Minutes()
	penalty := int(minutesSinceUpdate/10.0) + 1
	if penalty < 1 {
		penalty = 1
	}

	s.secondary.expiration += penalty
	if s.secondary.expiration > 5 {
		s.secondary = nil
		return []int{s.primary.value}
	}

	return []int{s.primary.value, s.secondary.value}
}
