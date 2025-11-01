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

// ServerBase64Encode traverses the message body and encodes byte arrays into base64 strings based on the provided paths.
func ServerBase64Encode(message []any) error {
	if len(message) < 2 {
		return fmt.Errorf("invalid message: expected headers and body, got %d elements", len(message))
	}

	headers, err := ensureStringMap(message[0])
	if err != nil {
		return err
	}

	body, err := ensureStringKeyedMap(message[1])
	if err != nil {
		return err
	}

	base64Paths := headers["@base64_"]
	if base64Paths == nil {
		return nil
	}

	_, err = travelServerBase64Encode(body, base64Paths)
	return err
}

func travelServerBase64Encode(value any, base64Paths any) (any, error) {
	switch paths := base64Paths.(type) {
	case map[string]any:
		for key, descriptor := range paths {
			if err := applyBase64EncodeDescriptor(value, key, descriptor); err != nil {
				return nil, err
			}
		}
		return value, nil
	case map[any]any:
		for rawKey, descriptor := range paths {
			key := fmt.Sprint(rawKey)
			if err := applyBase64EncodeDescriptor(value, key, descriptor); err != nil {
				return nil, err
			}
		}
		return value, nil
	case bool:
		if !paths {
			return nil, fmt.Errorf("invalid base64 path: %v for value: %v", base64Paths, value)
		}
		if value == nil {
			return nil, nil
		}
		bytesValue, ok := value.([]byte)
		if !ok {
			return nil, fmt.Errorf("invalid base64 path: %v for value: %T", base64Paths, value)
		}
		return base64.StdEncoding.EncodeToString(bytesValue), nil
	default:
		return nil, fmt.Errorf("invalid base64 path: %v for value: %v", base64Paths, value)
	}
}

func applyBase64EncodeDescriptor(container any, key string, descriptor any) error {
	if boolDescriptor, ok := descriptor.(bool); ok {
		if !boolDescriptor {
			return fmt.Errorf("invalid base64 path: %v for value: %v", key, container)
		}
		return applyBase64EncodeLeaf(container, key)
	}

	return applyBase64EncodeNested(container, key, descriptor)
}

func applyBase64EncodeLeaf(container any, key string) error {
	switch typed := container.(type) {
	case []any:
		if key != "*" {
			return fmt.Errorf("invalid base64 path: %s for value: %v", key, container)
		}
		for i, item := range typed {
			encoded, err := travelServerBase64Encode(item, true)
			if err != nil {
				return err
			}
			typed[i] = encoded
		}
		return nil
	case map[string]any:
		if key == "*" {
			for childKey, item := range typed {
				encoded, err := travelServerBase64Encode(item, true)
				if err != nil {
					return err
				}
				typed[childKey] = encoded
			}
			return nil
		}
		child, ok := typed[key]
		if !ok {
			return fmt.Errorf("invalid base64 path: %s for value: %v", key, container)
		}
		encoded, err := travelServerBase64Encode(child, true)
		if err != nil {
			return err
		}
		typed[key] = encoded
		return nil
	case map[any]any:
		if key == "*" {
			for childKey, item := range typed {
				encoded, err := travelServerBase64Encode(item, true)
				if err != nil {
					return err
				}
				typed[childKey] = encoded
			}
			return nil
		}
		child, ok := typed[key]
		if !ok {
			return fmt.Errorf("invalid base64 path: %s for value: %v", key, container)
		}
		encoded, err := travelServerBase64Encode(child, true)
		if err != nil {
			return err
		}
		typed[key] = encoded
		return nil
	default:
		return fmt.Errorf("invalid base64 path: %s for value: %v", key, container)
	}
}

func applyBase64EncodeNested(container any, key string, descriptor any) error {
	switch typed := container.(type) {
	case []any:
		if key != "*" {
			return fmt.Errorf("invalid base64 path: %s for value: %v", key, container)
		}
		for _, item := range typed {
			if _, err := travelServerBase64Encode(item, descriptor); err != nil {
				return err
			}
		}
		return nil
	case map[string]any:
		if key == "*" {
			for childKey, item := range typed {
				if updated, err := travelServerBase64Encode(item, descriptor); err != nil {
					return err
				} else if updated != nil {
					typed[childKey] = updated
				}
			}
			return nil
		}
		child, ok := typed[key]
		if !ok {
			return fmt.Errorf("invalid base64 path: %s for value: %v", key, container)
		}
		if updated, err := travelServerBase64Encode(child, descriptor); err != nil {
			return err
		} else if updated != nil {
			typed[key] = updated
		}
		return nil
	case map[any]any:
		if key == "*" {
			for childKey, item := range typed {
				if updated, err := travelServerBase64Encode(item, descriptor); err != nil {
					return err
				} else if updated != nil {
					typed[childKey] = updated
				}
			}
			return nil
		}
		child, ok := typed[key]
		if !ok {
			return fmt.Errorf("invalid base64 path: %s for value: %v", key, container)
		}
		if updated, err := travelServerBase64Encode(child, descriptor); err != nil {
			return err
		} else if updated != nil {
			typed[key] = updated
		}
		return nil
	default:
		return fmt.Errorf("invalid base64 path: %s for value: %v", key, container)
	}
}

func ensureStringKeyedMap(value any) (map[string]any, error) {
	switch typed := value.(type) {
	case map[string]any:
		return typed, nil
	case map[any]any:
		result := make(map[string]any, len(typed))
		for key, val := range typed {
			result[fmt.Sprint(key)] = val
		}
		return result, nil
	default:
		return nil, fmt.Errorf("expected map[string]any, got %T", value)
	}
}
