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

import "github.com/vmihailenco/msgpack/v5"

const (
// PackedByte is the msgpack extension type used to denote a packed list header.
PackedByte byte = 17
// UndefinedByte is the msgpack extension type used for undefined cells in packed rows.
UndefinedByte byte = 18
)

var (
packedListMarker = &packedListExt{}
undefinedMarker  = &undefinedExt{}
)

type packedListExt struct{}

func (p *packedListExt) MarshalMsgpack() ([]byte, error) {
return nil, nil
}

func (p *packedListExt) UnmarshalMsgpack([]byte) error {
return nil
}

type undefinedExt struct{}

func (u *undefinedExt) MarshalMsgpack() ([]byte, error) {
return nil, nil
}

func (u *undefinedExt) UnmarshalMsgpack([]byte) error {
return nil
}

func init() {
msgpack.RegisterExt(int8(PackedByte), (*packedListExt)(nil))
msgpack.RegisterExt(int8(UndefinedByte), (*undefinedExt)(nil))
}

// PackList packs a list of maps using a precomputed header.
func PackList(lst []any, header BinaryPackHeader) ([]any, error) {
if len(lst) == 0 {
return lst, nil
}

packedList := []any{packedListMarker}
for _, item := range lst {
mapValue, err := ensureAnyMap(item)
if err != nil {
return lst, nil
}

row, err := packRow(mapValue, header)
if err != nil {
return nil, err
}
packedList = append(packedList, row)
}

return packedList, nil
}

func packRow(m map[any]any, header BinaryPackHeader) ([]any, error) {
row := make([]any, len(header)-1)
for i := 1; i < len(header); i++ {
headerEntry := header[i]
key := headerEntry
if nestedHeader, ok := headerEntry.([]any); ok && len(nestedHeader) > 0 {
key = nestedHeader[0]
}

value, ok := m[key]
if !ok {
row[i-1] = undefinedMarker
continue
}

if nestedHeader, ok := headerEntry.([]any); ok {
nestedMap, err := ensureAnyMap(value)
if err != nil {
row[i-1] = value
continue
}
packedValue, err := packRow(nestedMap, BinaryPackHeader(nestedHeader))
if err != nil {
return nil, err
}
row[i-1] = packedValue
} else {
row[i-1] = value
}
}

for len(row) > 0 {
if _, ok := row[len(row)-1].(*undefinedExt); ok {
row = row[:len(row)-1]
continue
}
break
}

return row, nil
}
