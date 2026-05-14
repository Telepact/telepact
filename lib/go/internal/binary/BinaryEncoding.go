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

func (e *BinaryEncoding) decodeKey(key int) (string, bool) {
	if e == nil || key < 0 || key >= len(e.DecodeTable) {
		return "", false
	}
	return e.DecodeTable[key], true
}
