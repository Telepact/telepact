//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
