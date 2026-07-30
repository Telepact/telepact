//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

import "fmt"

// DecodeBody decodes a binary-encoded message body into pseudo-JSON using the provided BinaryEncoding.
func DecodeBody(encodedBody map[any]any, encoding *BinaryEncoding) (map[string]any, error) {
	decoded, err := DecodeKeys(encodedBody, encoding)
	if err != nil {
		return nil, err
	}

	result, ok := decoded.(map[string]any)
	if !ok {
		return nil, fmt.Errorf("expected decoded body to be map[string]any, got %T", decoded)
	}

	return result, nil
}
