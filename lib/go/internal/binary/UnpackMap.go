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

// UnpackMap converts a packed row into a map keyed by integers.
func UnpackMap(row []any, header []any) (map[int]any, error) {
	result := make(map[int]any)

	for idx := 0; idx < len(row); idx++ {
		keyIndex := idx + 1
		if keyIndex >= len(header) {
			return nil, fmt.Errorf("packed map header out of range for index %d", idx)
		}

		headerValue := header[keyIndex]
		value := row[idx]

		if _, skip := value.(*undefinedExt); skip {
			continue
		}

		if nestedHeader, ok := headerValue.([]any); ok {
			nestedRow, ok := value.([]any)
			if !ok {
				return nil, fmt.Errorf("expected nested packed row, got %T", value)
			}

			if len(nestedHeader) == 0 {
				return nil, fmt.Errorf("nested header missing key reference")
			}

			nestedKeyRaw := nestedHeader[0]
			nestedKey, ok := toInt(nestedKeyRaw)
			if !ok {
				return nil, fmt.Errorf("invalid nested key type: %T", nestedKeyRaw)
			}

			unpackedNested, err := UnpackMap(nestedRow, nestedHeader)
			if err != nil {
				return nil, err
			}

			result[nestedKey] = unpackedNested
			continue
		}

		key, ok := toInt(headerValue)
		if !ok {
			return nil, fmt.Errorf("invalid header key type: %T", headerValue)
		}

		unpackedValue, err := Unpack(value)
		if err != nil {
			return nil, err
		}

		result[key] = unpackedValue
	}

	return result, nil
}
