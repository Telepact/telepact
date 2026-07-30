//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

import "sort"

// PackMap attempts to pack a dictionary with integer keys into a compact row representation.
func PackMap(m map[int]any, header *[]any, keyIndexMap map[int]*BinaryPackNode) ([]any, error) {
	row := make([]any, 0, len(m))

	keys := make([]int, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Ints(keys)

	for _, key := range keys {
		rawValue := m[key]
		node, exists := keyIndexMap[key]
		if !exists {
			node = NewBinaryPackNode(len(*header)-1, make(map[int]*BinaryPackNode))

			if _, ok := toIntKeyMap(rawValue); ok {
				*header = append(*header, []any{key})
			} else {
				*header = append(*header, key)
			}

			keyIndexMap[key] = node
		}

		index := node.Value

		if mapValue, ok := toIntKeyMap(rawValue); ok {
			nestedHeaderAny := (*header)[index+1]
			nestedHeader, ok := nestedHeaderAny.([]any)
			if !ok {
				return nil, CannotPack{}
			}

			nestedMap := node.Nested
			if nestedMap == nil {
				nestedMap = make(map[int]*BinaryPackNode)
				node.Nested = nestedMap
			}

			nestedHeaderCopy := nestedHeader
			nestedRow, err := PackMap(mapValue, &nestedHeaderCopy, nestedMap)
			if err != nil {
				return nil, err
			}
			(*header)[index+1] = nestedHeaderCopy

			row = ensureRowCapacity(row, index)
			if len(row) == index {
				row = append(row, nestedRow)
			} else {
				row[index] = nestedRow
			}
		} else {
			if _, ok := (*header)[index+1].([]any); ok {
				return nil, CannotPack{}
			}

			packedValue, err := Pack(rawValue)
			if err != nil {
				return nil, err
			}

			row = ensureRowCapacity(row, index)
			if len(row) == index {
				row = append(row, packedValue)
			} else {
				row[index] = packedValue
			}
		}
	}

	return row, nil
}

func ensureRowCapacity(row []any, index int) []any {
	for len(row) < index {
		row = append(row, undefinedMarker)
	}
	return row
}
