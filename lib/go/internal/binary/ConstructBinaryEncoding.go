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

import (
"sort"
"strings"

"github.com/telepact/telepact/lib/go/internal/types"
)

// ConstructBinaryEncoding builds a BinaryEncoding from the supplied parsed Telepact schema types.
func ConstructBinaryEncoding(parsed map[string]types.TType) (*BinaryEncoding, error) {
allKeys := make(map[string]struct{})

for key, value := range parsed {
unionType, ok := value.(*types.TUnion)
if !ok {
continue
}

if strings.HasSuffix(key, ".->") {
resultStruct, ok := unionType.Tags["Ok_"]
if !ok {
continue
}

allKeys["Ok_"] = struct{}{}
appendStructKeys(resultStruct.Fields, allKeys)
} else if strings.HasPrefix(key, "fn.") {
allKeys[key] = struct{}{}

argsStruct, ok := unionType.Tags[key]
if !ok {
continue
}

appendStructKeys(argsStruct.Fields, allKeys)
}
}

sortedKeys := make([]string, 0, len(allKeys))
for key := range allKeys {
sortedKeys = append(sortedKeys, key)
}
sort.Strings(sortedKeys)

encodingMap := make(map[string]int, len(sortedKeys))
for index, key := range sortedKeys {
encodingMap[key] = index
}

packedSites := make([]BinaryPackSiteData, 0)
for key, value := range parsed {
unionType, ok := value.(*types.TUnion)
if !ok {
continue
}

if strings.HasSuffix(key, ".->") {
resultStruct, ok := unionType.Tags["Ok_"]
if ok {
addRootPackedSites([]string{"Ok_"}, resultStruct.Fields, encodingMap, &packedSites)
}
} else if strings.HasPrefix(key, "fn.") {
argsStruct, ok := unionType.Tags[key]
if ok {
addRootPackedSites([]string{key}, argsStruct.Fields, encodingMap, &packedSites)
}
}
}

checksum := CreateChecksum(strings.Join(sortedKeys, "\n"))
return NewBinaryEncoding(encodingMap, checksum, packedSites), nil
}

func appendStructKeys(fields map[string]*types.TFieldDeclaration, allKeys map[string]struct{}) {
for fieldKey, field := range fields {
allKeys[fieldKey] = struct{}{}
for _, nestedKey := range traceType(field.TypeDeclaration, map[string]struct{}{}) {
allKeys[nestedKey] = struct{}{}
}
}
}

func traceType(typeDeclaration *types.TTypeDeclaration, visitedTypeNames map[string]struct{}) []string {
if typeDeclaration == nil {
return nil
}

var keys []string

switch typed := typeDeclaration.Type.(type) {
case *types.TArray:
if len(typeDeclaration.TypeParameters) > 0 {
keys = append(keys, traceType(typeDeclaration.TypeParameters[0], visitedTypeNames)...)
}
case *types.TObject:
if len(typeDeclaration.TypeParameters) > 0 {
keys = append(keys, traceType(typeDeclaration.TypeParameters[0], visitedTypeNames)...)
}
case *types.TStruct:
if _, seen := visitedTypeNames[typed.Name]; seen {
return keys
}
nextVisited := copyVisitedTypeNames(visitedTypeNames)
nextVisited[typed.Name] = struct{}{}
for structFieldKey, structField := range typed.Fields {
keys = append(keys, structFieldKey)
keys = append(keys, traceType(structField.TypeDeclaration, nextVisited)...)
}
case *types.TUnion:
if _, seen := visitedTypeNames[typed.Name]; seen {
return keys
}
nextVisited := copyVisitedTypeNames(visitedTypeNames)
nextVisited[typed.Name] = struct{}{}
for tagKey, tagStruct := range typed.Tags {
keys = append(keys, tagKey)
for structFieldKey, structField := range tagStruct.Fields {
keys = append(keys, structFieldKey)
keys = append(keys, traceType(structField.TypeDeclaration, nextVisited)...)
}
}
}

return keys
}

func isDeterministicPackedStruct(typeDeclaration *types.TTypeDeclaration, visitingTypeNames map[string]struct{}) bool {
if typeDeclaration == nil {
return true
}

switch typed := typeDeclaration.Type.(type) {
case *types.TArray:
if len(typeDeclaration.TypeParameters) == 0 {
return true
}
switch typeDeclaration.TypeParameters[0].Type.(type) {
case *types.TStruct, *types.TUnion:
return false
default:
return true
}
case *types.TObject:
return true
case *types.TStruct:
if _, seen := visitingTypeNames[typed.Name]; seen {
return false
}
nextVisiting := copyVisitedTypeNames(visitingTypeNames)
nextVisiting[typed.Name] = struct{}{}
for _, field := range typed.Fields {
if !isDeterministicPackedStruct(field.TypeDeclaration, nextVisiting) {
return false
}
}
return true
case *types.TUnion:
if _, seen := visitingTypeNames[typed.Name]; seen {
return false
}
nextVisiting := copyVisitedTypeNames(visitingTypeNames)
nextVisiting[typed.Name] = struct{}{}
for _, tagStruct := range typed.Tags {
for _, field := range tagStruct.Fields {
if !isDeterministicPackedStruct(field.TypeDeclaration, nextVisiting) {
return false
}
}
}
return true
default:
return true
}
}

func buildPackHeader(structType *types.TStruct, encodingMap map[string]int) BinaryPackHeader {
header := BinaryPackHeader{nil}
for fieldKey, field := range structType.Fields {
header = append(header, buildNestedHeader(fieldKey, field.TypeDeclaration, encodingMap))
}
return header
}

func buildNestedHeader(key string, typeDeclaration *types.TTypeDeclaration, encodingMap map[string]int) any {
encodedKey := encodingMap[key]
if typeDeclaration == nil {
return encodedKey
}

switch typed := typeDeclaration.Type.(type) {
case *types.TStruct:
header := BinaryPackHeader{encodedKey}
for fieldKey, field := range typed.Fields {
header = append(header, buildNestedHeader(fieldKey, field.TypeDeclaration, encodingMap))
}
return header
case *types.TUnion:
header := BinaryPackHeader{encodedKey}
for tagKey, tagStruct := range typed.Tags {
tagHeader := BinaryPackHeader{encodingMap[tagKey]}
for fieldKey, field := range tagStruct.Fields {
tagHeader = append(tagHeader, buildNestedHeader(fieldKey, field.TypeDeclaration, encodingMap))
}
header = append(header, tagHeader)
}
return header
default:
return encodedKey
}
}

func collectPackedSites(path []string, typeDeclaration *types.TTypeDeclaration, encodingMap map[string]int, packedSites *[]BinaryPackSiteData, visitedTypeNames map[string]struct{}) {
if typeDeclaration == nil {
return
}

switch typed := typeDeclaration.Type.(type) {
case *types.TArray:
if len(typeDeclaration.TypeParameters) == 0 {
return
}
if structType, ok := typeDeclaration.TypeParameters[0].Type.(*types.TStruct); ok && isDeterministicPackedStruct(typeDeclaration.TypeParameters[0], map[string]struct{}{}) {
*packedSites = append(*packedSites, BinaryPackSiteData{
Path:   append([]string{}, path...),
Header: buildPackHeader(structType, encodingMap),
})
}
case *types.TObject:
return
case *types.TStruct:
if _, seen := visitedTypeNames[typed.Name]; seen {
return
}
nextVisited := copyVisitedTypeNames(visitedTypeNames)
nextVisited[typed.Name] = struct{}{}
for fieldKey, field := range typed.Fields {
collectPackedSites(append(path, fieldKey), field.TypeDeclaration, encodingMap, packedSites, nextVisited)
}
case *types.TUnion:
if _, seen := visitedTypeNames[typed.Name]; seen {
return
}
nextVisited := copyVisitedTypeNames(visitedTypeNames)
nextVisited[typed.Name] = struct{}{}
for tagKey, tagStruct := range typed.Tags {
for fieldKey, field := range tagStruct.Fields {
collectPackedSites(append(append(path, tagKey), fieldKey), field.TypeDeclaration, encodingMap, packedSites, nextVisited)
}
}
}
}

func addRootPackedSites(rootPath []string, fields map[string]*types.TFieldDeclaration, encodingMap map[string]int, packedSites *[]BinaryPackSiteData) {
for fieldKey, field := range fields {
collectPackedSites(append(rootPath, fieldKey), field.TypeDeclaration, encodingMap, packedSites, map[string]struct{}{})
}
}

func copyVisitedTypeNames(input map[string]struct{}) map[string]struct{} {
result := make(map[string]struct{}, len(input))
for key := range input {
result[key] = struct{}{}
}
return result
}
