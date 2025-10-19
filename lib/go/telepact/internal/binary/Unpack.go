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

// Unpack recursively unpacks packed lists and maps back into pseudo-JSON structures.
func Unpack(value any) (any, error) {
	switch typed := value.(type) {
	case []any:
		return UnpackList(typed)
	case map[any]any:
		result := make(map[any]any, len(typed))
		for key, val := range typed {
			unpacked, err := Unpack(val)
			if err != nil {
				return nil, err
			}
			result[key] = unpacked
		}
		return result, nil
	case map[string]any:
		result := make(map[string]any, len(typed))
		for key, val := range typed {
			unpacked, err := Unpack(val)
			if err != nil {
				return nil, err
			}
			result[key] = unpacked
		}
		return result, nil
	case map[int]any:
		result := make(map[int]any, len(typed))
		for key, val := range typed {
			unpacked, err := Unpack(val)
			if err != nil {
				return nil, err
			}
			result[key] = unpacked
		}
		return result, nil
	default:
		return value, nil
	}
}
