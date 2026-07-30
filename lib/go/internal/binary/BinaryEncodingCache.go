//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// BinaryEncodingCache stores BinaryEncoding instances keyed by checksum values.
type BinaryEncodingCache interface {
	// Add registers a BinaryEncoding entry for the provided checksum.
	Add(checksum int, binaryEncodingMap map[string]int)
	// Get retrieves the BinaryEncoding associated with the checksum.
	Get(checksum int) *BinaryEncoding
	// Remove deletes the BinaryEncoding associated with the checksum.
	Remove(checksum int)
}
