//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

import "fmt"

// EncodeBody encodes a pseudo-JSON message body with the provided BinaryEncoding lookup tables.
func EncodeBody(messageBody map[string]any, encoding *BinaryEncoding) (map[any]any, error) {
	encoded, err := EncodeKeys(messageBody, encoding)
	if err != nil {
		return nil, err
	}

	result, ok := encoded.(map[any]any)
	if !ok {
		return nil, fmt.Errorf("expected encoded body to be map[any]any, got %T", encoded)
	}

	return result, nil
}
