//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
