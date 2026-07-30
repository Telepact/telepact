//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// PackBody packs the message body map into the compact binary representation when possible.
func PackBody(body map[any]any) (map[any]any, error) {
	result := make(map[any]any, len(body))
	for key, value := range body {
		packedValue, err := Pack(value)
		if err != nil {
			return nil, err
		}
		result[key] = packedValue
	}
	return result, nil
}
