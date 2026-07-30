//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

import "fmt"

// BinaryEncodingMissing indicates that an expected key was absent from the binary encoding map.
type BinaryEncodingMissing struct {
	Key any
}

// NewBinaryEncodingMissing constructs a BinaryEncodingMissing error for the provided key.
func NewBinaryEncodingMissing(key any) *BinaryEncodingMissing {
	return &BinaryEncodingMissing{Key: key}
}

// Error implements the error interface.
func (e *BinaryEncodingMissing) Error() string {
	if e == nil {
		return "missing binary encoding"
	}
	return fmt.Sprintf("Missing binary encoding for %v", e.Key)
}
