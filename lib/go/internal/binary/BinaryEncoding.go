//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// BinaryEncoding stores lookup tables for translating between string keys and integer codes
// in the binary encoding representation.
type BinaryEncoding struct {
	EncodeMap map[string]int
	DecodeMap map[int]string
	Checksum  int
}

// NewBinaryEncoding constructs a BinaryEncoding from the provided encoding map and checksum.
func NewBinaryEncoding(binaryEncodingMap map[string]int, checksum int) *BinaryEncoding {
	encodeMap := make(map[string]int, len(binaryEncodingMap))
	for key, value := range binaryEncodingMap {
		encodeMap[key] = value
	}

	decodeMap := make(map[int]string, len(binaryEncodingMap))
	for key, value := range encodeMap {
		decodeMap[value] = key
	}

	return &BinaryEncoding{
		EncodeMap: encodeMap,
		DecodeMap: decodeMap,
		Checksum:  checksum,
	}
}
