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
			newKey, err := decodeIntegerKey(key, encoding)
			if err != nil {
				return nil, err
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
				newKey, err := decodeIntegerKey(intKey, encoding)
				if err != nil {
					return nil, err
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
			if decoded, err := decodeIntegerKey(intKey, encoding); err == nil {
				return decoded, true, nil
			} else {
				return "", false, err
			}
		}
	}
	return "", false, nil
}

func decodeIntegerKey(key int, encoding *BinaryEncoding) (decodedKey string, err error) {
	defer func() {
		if recovered := recover(); recovered != nil {
			err = NewBinaryEncodingMissing(key)
		}
	}()
	return encoding.DecodeTable[key], nil
}
