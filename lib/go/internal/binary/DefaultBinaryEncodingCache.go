//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
