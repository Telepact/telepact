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

// UnpackBody unpacks each entry within the message body map.
func UnpackBody(body map[any]any, encoding *BinaryEncoding) (map[any]any, error) {
result := make(map[any]any, len(body))
for key, value := range body {
result[key] = value
}

for _, packedSite := range encoding.PackedSites {
parentMap, ok := getParentMap(result, packedSite.EncodedPath)
if !ok || len(packedSite.EncodedPath) == 0 {
continue
}
targetKey := packedSite.EncodedPath[len(packedSite.EncodedPath)-1]
value, ok := parentMap[targetKey]
if !ok {
continue
}
listValue, ok := value.([]any)
if !ok {
continue
}
unpackedValue, err := UnpackList(listValue, packedSite.Header)
if err != nil {
return nil, err
}
parentMap[targetKey] = unpackedValue
}

return result, nil
}
