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

// ServerBase64Decode traverses the message body and decodes base64 strings into byte arrays based on the provided paths.
func ServerBase64Decode(body map[string]any, bytesPaths map[string]any) error {
	_, err := travelServerBase64Decode(body, bytesPaths)
	return err
}

func travelServerBase64Decode(value any, bytesPaths any) (any, error) {
	switch paths := bytesPaths.(type) {
	case map[string]any:
		for key, descriptor := range paths {
			if err := applyBase64DecodeDescriptor(value, key, descriptor); err != nil {
				return nil, err
			}
		}
		return value, nil
	case map[any]any:
		for rawKey, descriptor := range paths {
			key := fmt.Sprint(rawKey)
			if err := applyBase64DecodeDescriptor(value, key, descriptor); err != nil {
				return nil, err
			}
		}
		return value, nil
	case bool:
		if !paths {
			return nil, fmt.Errorf("invalid bytes path: %v for value: %v", bytesPaths, value)
		}
		if value == nil {
			return nil, nil
		}
		str, ok := value.(string)
		if !ok {
			return nil, fmt.Errorf("invalid bytes path: %v for value: %T", bytesPaths, value)
		}
		decoded, err := base64.StdEncoding.DecodeString(str)
		if err != nil {
			return nil, err
		}
		return decoded, nil
	default:
		return nil, fmt.Errorf("invalid bytes path: %v for value: %v", bytesPaths, value)
	}
}

func applyBase64DecodeDescriptor(container any, key string, descriptor any) error {
	if boolDescriptor, ok := descriptor.(bool); ok {
		if !boolDescriptor {
			return fmt.Errorf("invalid bytes path: %v for value: %v", key, container)
		}
		return applyBase64DecodeLeaf(container, key)
	}

	return applyBase64DecodeNested(container, key, descriptor)
}

func applyBase64DecodeLeaf(container any, key string) error {
	switch typed := container.(type) {
	case []any:
		if key != "*" {
			return fmt.Errorf("invalid bytes path: %s for value: %v", key, container)
		}
		for i, item := range typed {
			decoded, err := travelServerBase64Decode(item, true)
			if err != nil {
				return err
			}
			typed[i] = decoded
		}
		return nil
	case map[string]any:
		if key == "*" {
			for childKey, item := range typed {
				decoded, err := travelServerBase64Decode(item, true)
				if err != nil {
					return err
				}
				typed[childKey] = decoded
			}
			return nil
		}
		child, ok := typed[key]
		if !ok {
			return fmt.Errorf("invalid bytes path: %s for value: %v", key, container)
		}
		decoded, err := travelServerBase64Decode(child, true)
		if err != nil {
			return err
		}
		typed[key] = decoded
		return nil
	case map[any]any:
		if key == "*" {
			for childKey, item := range typed {
				decoded, err := travelServerBase64Decode(item, true)
				if err != nil {
					return err
				}
				typed[childKey] = decoded
			}
			return nil
		}
		child, ok := typed[key]
		if !ok {
			return fmt.Errorf("invalid bytes path: %s for value: %v", key, container)
		}
		decoded, err := travelServerBase64Decode(child, true)
		if err != nil {
			return err
		}
		typed[key] = decoded
		return nil
	default:
		return fmt.Errorf("invalid bytes path: %s for value: %v", key, container)
	}
}

func applyBase64DecodeNested(container any, key string, descriptor any) error {
	switch typed := container.(type) {
	case []any:
		if key != "*" {
			return fmt.Errorf("invalid bytes path: %s for value: %v", key, container)
		}
		for _, item := range typed {
			if _, err := travelServerBase64Decode(item, descriptor); err != nil {
				return err
			}
		}
		return nil
	case map[string]any:
		if key == "*" {
			for childKey, item := range typed {
				if updated, err := travelServerBase64Decode(item, descriptor); err != nil {
					return err
				} else if updated != nil {
					typed[childKey] = updated
				}
			}
			return nil
		}
		child, ok := typed[key]
		if !ok {
			return fmt.Errorf("invalid bytes path: %s for value: %v", key, container)
		}
		if updated, err := travelServerBase64Decode(child, descriptor); err != nil {
			return err
		} else if updated != nil {
			typed[key] = updated
		}
		return nil
	case map[any]any:
		if key == "*" {
			for childKey, item := range typed {
				if updated, err := travelServerBase64Decode(item, descriptor); err != nil {
					return err
				} else if updated != nil {
					typed[childKey] = updated
				}
			}
			return nil
		}
		child, ok := typed[key]
		if !ok {
			return fmt.Errorf("invalid bytes path: %s for value: %v", key, container)
		}
		if updated, err := travelServerBase64Decode(child, descriptor); err != nil {
			return err
		} else if updated != nil {
			typed[key] = updated
		}
		return nil
	default:
		return fmt.Errorf("invalid bytes path: %s for value: %v", key, container)
	}
}
