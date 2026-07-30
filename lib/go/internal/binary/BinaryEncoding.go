//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// BinaryEncoding stores lookup tables for translating between string keys and integer codes
// in the binary encoding representation.
type BinaryEncoding struct {
	EncodeMap   map[string]int
	DecodeTable []string
	Checksum    int
}

// NewBinaryEncoding constructs a BinaryEncoding from the provided encoding map and checksum.
func NewBinaryEncoding(binaryEncodingMap map[string]int, checksum int) *BinaryEncoding {
	encodeMap := make(map[string]int, len(binaryEncodingMap))
	for key, value := range binaryEncodingMap {
		encodeMap[key] = value
	}

	decodeTable := make([]string, len(encodeMap))
	decodePresent := make([]bool, len(encodeMap))
	for key, value := range encodeMap {
		if value < 0 || value >= len(decodeTable) {
			panic("binary encoding ids must be dense sequential integers")
		}
		if decodePresent[value] {
			panic("binary encoding ids must be unique")
		}
		decodeTable[value] = key
		decodePresent[value] = true
	}
	for _, present := range decodePresent {
		if !present {
			panic("binary encoding ids must be dense sequential integers")
		}
	}

	return &BinaryEncoding{
		EncodeMap:   encodeMap,
		DecodeTable: decodeTable,
		Checksum:    checksum,
	}
}
