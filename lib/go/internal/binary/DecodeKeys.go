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
	"fmt"
	"strconv"
)

// DecodeKeys recursively decodes map keys using the provided BinaryEncoding lookup tables.
func DecodeKeys(given any, encoding *BinaryEncoding) (any, error) {
	switch typed := given.(type) {
	case map[string]any:
		result := make(map[string]any, len(typed))
		for key, value := range typed {
			decodedValue, err := DecodeKeys(value, encoding)
			if err != nil {
				return nil, err
			}
			if decodedKey, ok, convErr := decodeNumericStringKey(key, encoding); convErr != nil {
				return nil, convErr
			} else if ok {
				result[decodedKey] = decodedValue
				continue
			}
			result[key] = decodedValue
		}
		return result, nil
	case map[int]any:
		result := make(map[string]any, len(typed))
		for key, value := range typed {
			decodedValue, err := DecodeKeys(value, encoding)
			if err != nil {
				return nil, err
			}
			newKey, ok := encoding.DecodeMap[key]
			if !ok {
				return nil, NewBinaryEncodingMissing(key)
			}
			result[newKey] = decodedValue
		}
		return result, nil
	case map[any]any:
		result := make(map[string]any, len(typed))
		for rawKey, value := range typed {
			decodedValue, err := DecodeKeys(value, encoding)
			if err != nil {
				return nil, err
			}

			switch key := rawKey.(type) {
			case string:
				if decodedKey, ok, convErr := decodeNumericStringKey(key, encoding); convErr != nil {
					return nil, convErr
				} else if ok {
					result[decodedKey] = decodedValue
					break
				}
				result[key] = decodedValue
			default:
				intKey, ok := toInt(key)
				if !ok {
					return nil, fmt.Errorf("invalid key type for decode: %T", rawKey)
				}
				newKey, exists := encoding.DecodeMap[intKey]
				if !exists {
					return nil, NewBinaryEncodingMissing(intKey)
				}
				result[newKey] = decodedValue
			}
		}
		return result, nil
	case []any:
		result := make([]any, len(typed))
		for i, item := range typed {
			decodedValue, err := DecodeKeys(item, encoding)
			if err != nil {
				return nil, err
			}
			result[i] = decodedValue
		}
		return result, nil
	default:
		return given, nil
	}
}

func decodeNumericStringKey(key string, encoding *BinaryEncoding) (string, bool, error) {
	if encoding == nil {
		return "", false, nil
	}
	if len(key) == 0 {
		return "", false, nil
	}
	if key[0] == '-' || (key[0] >= '0' && key[0] <= '9') {
		if intKey, err := strconv.Atoi(key); err == nil {
			if decoded, ok := encoding.DecodeMap[intKey]; ok {
				return decoded, true, nil
			}
			return "", false, NewBinaryEncodingMissing(intKey)
		}
	}
	return "", false, nil
}
