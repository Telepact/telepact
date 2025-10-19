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

// ClientBase64Decode decodes base64-encoded payload fields specified by the pseudo-JSON headers.
func ClientBase64Decode(message []any) error {
	if len(message) < 2 {
		return fmt.Errorf("invalid message: expected headers and body, got %d elements", len(message))
	}

	var base64Paths any
	switch headers := message[0].(type) {
	case map[string]any:
		base64Paths = headers["@base64_"]
	case map[any]any:
		base64Paths = headers["@base64_"]
	default:
		return fmt.Errorf("invalid message headers for base64 decode: %T", message[0])
	}

	if base64Paths == nil {
		return nil
	}

	_, err := travelBase64Decode(message[1], base64Paths)
	return err
}

func travelBase64Decode(value any, base64Paths any) (any, error) {
	switch paths := base64Paths.(type) {
	case map[string]any:
		for key, descriptor := range paths {
			if err := applyBase64Descriptor(value, key, descriptor); err != nil {
				return nil, err
			}
		}
		return nil, nil
	case map[any]any:
		for rawKey, descriptor := range paths {
			key := fmt.Sprint(rawKey)
			if err := applyBase64Descriptor(value, key, descriptor); err != nil {
				return nil, err
			}
		}
		return nil, nil
	case bool:
		if !paths {
			return nil, invalidBase64Path(base64Paths, value)
		}
		if value == nil {
			return nil, nil
		}
		str, ok := value.(string)
		if !ok {
			return nil, invalidBase64Path(base64Paths, value)
		}
		decoded, err := base64.StdEncoding.DecodeString(str)
		if err != nil {
			return nil, fmt.Errorf("decode base64 value: %w", err)
		}
		return decoded, nil
	default:
		return nil, invalidBase64Path(base64Paths, value)
	}
}

func applyBase64Descriptor(container any, key string, descriptor any) error {
	if boolDescriptor, ok := descriptor.(bool); ok {
		if !boolDescriptor {
			return invalidBase64Path(descriptor, container)
		}
		if key == "*" {
			switch typed := container.(type) {
			case []any:
				for i, item := range typed {
					decoded, err := travelBase64Decode(item, true)
					if err != nil {
						return err
					}
					typed[i] = decoded
				}
				return nil
			case map[string]any:
				for k, item := range typed {
					decoded, err := travelBase64Decode(item, true)
					if err != nil {
						return err
					}
					typed[k] = decoded
				}
				return nil
			case map[any]any:
				for k, item := range typed {
					decoded, err := travelBase64Decode(item, true)
					if err != nil {
						return err
					}
					typed[k] = decoded
				}
				return nil
			default:
				return invalidBase64Path(key, container)
			}
		}
		switch typed := container.(type) {
		case map[string]any:
			child, ok := typed[key]
			if !ok {
				return invalidBase64Path(key, container)
			}
			decoded, err := travelBase64Decode(child, true)
			if err != nil {
				return err
			}
			typed[key] = decoded
			return nil
		case map[any]any:
			child, ok := typed[key]
			if !ok {
				return invalidBase64Path(key, container)
			}
			decoded, err := travelBase64Decode(child, true)
			if err != nil {
				return err
			}
			typed[key] = decoded
			return nil
		default:
			return invalidBase64Path(key, container)
		}
	}

	if key == "*" {
		switch typed := container.(type) {
		case []any:
			for i := range typed {
				if _, err := travelBase64Decode(typed[i], descriptor); err != nil {
					return err
				}
			}
			return nil
		case map[string]any:
			for k := range typed {
				if _, err := travelBase64Decode(typed[k], descriptor); err != nil {
					return err
				}
			}
			return nil
		case map[any]any:
			for k := range typed {
				if _, err := travelBase64Decode(typed[k], descriptor); err != nil {
					return err
				}
			}
			return nil
		default:
			return invalidBase64Path(key, container)
		}
	}

	switch typed := container.(type) {
	case map[string]any:
		child, ok := typed[key]
		if !ok {
			return invalidBase64Path(key, container)
		}
		if _, err := travelBase64Decode(child, descriptor); err != nil {
			return err
		}
		return nil
	case map[any]any:
		child, ok := typed[key]
		if !ok {
			return invalidBase64Path(key, container)
		}
		if _, err := travelBase64Decode(child, descriptor); err != nil {
			return err
		}
		return nil
	default:
		return invalidBase64Path(key, container)
	}
}

func invalidBase64Path(base64Paths any, value any) error {
	return fmt.Errorf("invalid base64 path: %v for value: %v", base64Paths, value)
}
