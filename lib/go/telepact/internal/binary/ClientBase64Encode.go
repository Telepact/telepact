//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
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
