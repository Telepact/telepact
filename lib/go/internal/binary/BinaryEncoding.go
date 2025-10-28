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
