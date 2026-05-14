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

import "fmt"

type BinaryPackHeader []any

type BinaryPackSiteData struct {
Path   []string
Header BinaryPackHeader
}

type BinaryPackSite struct {
Path        []string
EncodedPath []int
Header      BinaryPackHeader
}

func cloneBinaryPackHeader(header BinaryPackHeader) BinaryPackHeader {
result := make(BinaryPackHeader, len(header))
for i, entry := range header {
if nested, ok := entry.([]any); ok {
result[i] = cloneBinaryPackHeader(BinaryPackHeader(nested))
} else {
result[i] = entry
}
}
return result
}

func newBinaryPackSite(site BinaryPackSiteData, binaryEncodingMap map[string]int) (*BinaryPackSite, error) {
encodedPath := make([]int, len(site.Path))
for i, segment := range site.Path {
encodedSegment, ok := binaryEncodingMap[segment]
if !ok {
return nil, fmt.Errorf("missing binary encoding for packed path segment %s", segment)
}
encodedPath[i] = encodedSegment
}

return &BinaryPackSite{
Path:        append([]string{}, site.Path...),
EncodedPath: encodedPath,
Header:      cloneBinaryPackHeader(site.Header),
}, nil
}

func (s *BinaryPackSite) ToData() []any {
return []any{append([]string{}, s.Path...), cloneBinaryPackHeader(s.Header)}
}

// BinaryEncoding stores lookup tables for translating between string keys and integer codes
// in the binary encoding representation.
type BinaryEncoding struct {
EncodeMap   map[string]int
DecodeTable []string
Checksum    int
PackedSites []*BinaryPackSite
}

// NewBinaryEncoding constructs a BinaryEncoding from the provided encoding map and checksum.
func NewBinaryEncoding(binaryEncodingMap map[string]int, checksum int, packedSites []BinaryPackSiteData) *BinaryEncoding {
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

compiledPackedSites := make([]*BinaryPackSite, 0, len(packedSites))
for _, packedSite := range packedSites {
compiled, err := newBinaryPackSite(packedSite, encodeMap)
if err != nil {
panic(err)
}
compiledPackedSites = append(compiledPackedSites, compiled)
}

return &BinaryEncoding{
EncodeMap:   encodeMap,
DecodeTable: decodeTable,
Checksum:    checksum,
PackedSites: compiledPackedSites,
}
}

func (b *BinaryEncoding) PackedSiteData() []any {
result := make([]any, 0, len(b.PackedSites))
for _, packedSite := range b.PackedSites {
result = append(result, packedSite.ToData())
}
return result
}
