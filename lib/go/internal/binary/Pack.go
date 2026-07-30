//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// Pack attempts to pack nested maps/lists into the compact binary representation used by Telepact.
func Pack(value any) (any, error) {
	switch typed := value.(type) {
	case []any:
		return PackList(typed)
	case map[string]any:
		result := make(map[string]any, len(typed))
		for key, val := range typed {
			packed, err := Pack(val)
			if err != nil {
				return nil, err
			}
			result[key] = packed
		}
		return result, nil
	case map[int]any:
		result := make(map[int]any, len(typed))
		for key, val := range typed {
			packed, err := Pack(val)
			if err != nil {
				return nil, err
			}
			result[key] = packed
		}
		return result, nil
	case map[any]any:
		result := make(map[any]any, len(typed))
		for key, val := range typed {
			packed, err := Pack(val)
			if err != nil {
				return nil, err
			}
			result[key] = packed
		}
		return result, nil
	default:
		return value, nil
	}
}
