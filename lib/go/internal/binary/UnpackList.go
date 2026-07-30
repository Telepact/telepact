//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

import "fmt"

// UnpackList converts packed list representation back into standard pseudo-JSON arrays.
func UnpackList(lst []any) ([]any, error) {
	if len(lst) == 0 {
		return lst, nil
	}

	switch lst[0].(type) {
	case *packedListExt:
		if len(lst) < 2 {
			return nil, fmt.Errorf("invalid packed list: missing header")
		}

		header, ok := lst[1].([]any)
		if !ok {
			return nil, fmt.Errorf("invalid packed list header type: %T", lst[1])
		}

		unpacked := make([]any, 0, len(lst)-2)
		for i := 2; i < len(lst); i++ {
			row, ok := lst[i].([]any)
			if !ok {
				return nil, fmt.Errorf("invalid packed row type: %T", lst[i])
			}

			unpackedMap, err := UnpackMap(row, header)
			if err != nil {
				return nil, err
			}
			unpacked = append(unpacked, unpackedMap)
		}

		return unpacked, nil
	default:
		result := make([]any, len(lst))
		for i, item := range lst {
			unpacked, err := Unpack(item)
			if err != nil {
				return nil, err
			}
			result[i] = unpacked
		}
		return result, nil
	}
}
