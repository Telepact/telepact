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

import "fmt"

// EncodeKeys recursively encodes map keys using the provided BinaryEncoding lookup tables.
func EncodeKeys(given any, encoding *BinaryEncoding) (any, error) {
	switch typed := given.(type) {
	case nil:
		return nil, nil
	case map[string]any:
		result := make(map[any]any, len(typed))
		for key, value := range typed {
			encodedValue, err := EncodeKeys(value, encoding)
			if err != nil {
				return nil, err
			}

			if mapped, ok := encoding.EncodeMap[key]; ok {
				result[mapped] = encodedValue
			} else {
				result[key] = encodedValue
			}
		}
		return result, nil
	case map[int]any:
		result := make(map[int]any, len(typed))
		for key, value := range typed {
			encodedValue, err := EncodeKeys(value, encoding)
			if err != nil {
				return nil, err
			}
			result[key] = encodedValue
		}
		return result, nil
	case map[any]any:
		result := make(map[any]any, len(typed))
		for key, value := range typed {
			encodedValue, err := EncodeKeys(value, encoding)
			if err != nil {
				return nil, err
			}

			keyString := fmt.Sprint(key)
			if mapped, ok := encoding.EncodeMap[keyString]; ok {
				result[mapped] = encodedValue
			} else {
				result[key] = encodedValue
			}
		}
		return result, nil
	case []any:
		result := make([]any, len(typed))
		for i, item := range typed {
			encodedValue, err := EncodeKeys(item, encoding)
			if err != nil {
				return nil, err
			}
			result[i] = encodedValue
		}
		return result, nil
	default:
		return given, nil
	}
}
