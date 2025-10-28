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

// BinaryPackNode represents a node in the binary packing trie used to encode field keys.
type BinaryPackNode struct {
	Value  int
	Nested map[int]*BinaryPackNode
}

// NewBinaryPackNode constructs a BinaryPackNode with defensive copies of the nested map.
func NewBinaryPackNode(value int, nested map[int]*BinaryPackNode) *BinaryPackNode {
	var cloned map[int]*BinaryPackNode
	if nested != nil {
		cloned = make(map[int]*BinaryPackNode, len(nested))
		for key, child := range nested {
			cloned[key] = child
		}
	}
	return &BinaryPackNode{
		Value:  value,
		Nested: cloned,
	}
}
