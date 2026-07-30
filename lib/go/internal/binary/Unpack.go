//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// Unpack recursively unpacks packed lists and maps back into pseudo-JSON structures.
func Unpack(value any) (any, error) {
	switch typed := value.(type) {
	case []any:
		return UnpackList(typed)
	case map[any]any:
		result := make(map[any]any, len(typed))
		for key, val := range typed {
			unpacked, err := Unpack(val)
			if err != nil {
				return nil, err
			}
			result[key] = unpacked
		}
		return result, nil
	case map[string]any:
		result := make(map[string]any, len(typed))
		for key, val := range typed {
			unpacked, err := Unpack(val)
			if err != nil {
				return nil, err
			}
			result[key] = unpacked
		}
		return result, nil
	case map[int]any:
		result := make(map[int]any, len(typed))
		for key, val := range typed {
			unpacked, err := Unpack(val)
			if err != nil {
				return nil, err
			}
			result[key] = unpacked
		}
		return result, nil
	default:
		return value, nil
	}
}
