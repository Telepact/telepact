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

import "sync"

// DefaultBinaryEncodingCache stores recently used binary encoders in-memory.
type DefaultBinaryEncodingCache struct {
	mu    sync.RWMutex
	cache map[int]*BinaryEncoding
}

// NewDefaultBinaryEncodingCache constructs a DefaultBinaryEncodingCache instance.
func NewDefaultBinaryEncodingCache() *DefaultBinaryEncodingCache {
	return &DefaultBinaryEncodingCache{
		cache: make(map[int]*BinaryEncoding),
	}
}

// Add registers a BinaryEncoding for the provided checksum.
func (c *DefaultBinaryEncodingCache) Add(checksum int, binaryEncodingMap map[string]int) {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.cache == nil {
		c.cache = make(map[int]*BinaryEncoding)
	}

	encoding := NewBinaryEncoding(binaryEncodingMap, checksum)
	c.cache[checksum] = encoding
}

// Get retrieves the BinaryEncoding for the checksum, returning nil when absent.
func (c *DefaultBinaryEncodingCache) Get(checksum int) *BinaryEncoding {
	c.mu.RLock()
	defer c.mu.RUnlock()

	if c.cache == nil {
		return nil
	}
	return c.cache[checksum]
}

// Remove deletes the BinaryEncoding for the checksum.
func (c *DefaultBinaryEncodingCache) Remove(checksum int) {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.cache == nil {
		return
	}
	delete(c.cache, checksum)
}
