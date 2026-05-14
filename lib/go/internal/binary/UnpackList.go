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

// UnpackList converts packed list representation back into standard pseudo-JSON arrays.
func UnpackList(lst []any, header BinaryPackHeader) ([]any, error) {
if len(lst) == 0 {
return lst, nil
}

if _, ok := lst[0].(*packedListExt); !ok {
return lst, nil
}

unpacked := make([]any, 0, len(lst)-1)
for i := 1; i < len(lst); i++ {
row, ok := lst[i].([]any)
if !ok {
unpacked = append(unpacked, lst[i])
continue
}

unpackedMap, err := unpackRow(row, header)
if err != nil {
return nil, err
}
unpacked = append(unpacked, unpackedMap)
}

return unpacked, nil
}

func unpackRow(row []any, header BinaryPackHeader) (map[any]any, error) {
finalMap := make(map[any]any, len(row))
for i, value := range row {
if i+1 >= len(header) {
continue
}

headerEntry := header[i+1]
if _, ok := value.(*undefinedExt); ok {
continue
}

if nestedHeader, ok := headerEntry.([]any); ok {
nestedRow, ok := value.([]any)
if !ok || len(nestedHeader) == 0 {
continue
}
nestedMap, err := unpackRow(nestedRow, BinaryPackHeader(nestedHeader))
if err != nil {
return nil, err
}
finalMap[nestedHeader[0]] = nestedMap
} else {
finalMap[headerEntry] = value
}
}
return finalMap, nil
}
