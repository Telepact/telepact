//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// UnpackBody unpacks each entry within the message body map.
func UnpackBody(body map[any]any) (map[any]any, error) {
	result := make(map[any]any, len(body))
	for key, value := range body {
		unpacked, err := Unpack(value)
		if err != nil {
			return nil, err
		}
		result[key] = unpacked
	}
	return result, nil
}
