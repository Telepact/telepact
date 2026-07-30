//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

import (
	"encoding/base64"
	"fmt"
)

// ClientBase64Encode traverses the message body and encodes any raw byte slices into base64 strings.
func ClientBase64Encode(message []any) error {
	if len(message) < 2 {
		return fmt.Errorf("invalid message: expected headers and body, got %d elements", len(message))
	}

	encoded, err := travelBase64Encode(message[1])
	if err != nil {
		return err
	}

	message[1] = encoded
	return nil
}

func travelBase64Encode(value any) (any, error) {
	switch typed := value.(type) {
	case map[string]any:
		for key, item := range typed {
			encoded, err := travelBase64Encode(item)
			if err != nil {
				return nil, err
			}
			typed[key] = encoded
		}
		return typed, nil
	case map[any]any:
		for key, item := range typed {
			encoded, err := travelBase64Encode(item)
			if err != nil {
				return nil, err
			}
			typed[key] = encoded
		}
		return typed, nil
	case []any:
		for index, item := range typed {
			encoded, err := travelBase64Encode(item)
			if err != nil {
				return nil, err
			}
			typed[index] = encoded
		}
		return typed, nil
	case []byte:
		return base64.StdEncoding.EncodeToString(typed), nil
	case nil:
		return nil, nil
	default:
		return typed, nil
	}
}
