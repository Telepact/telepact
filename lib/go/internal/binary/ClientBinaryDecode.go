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

// ClientBinaryDecode decodes a Telepact client message using the provided binary encoding cache and strategy.
func ClientBinaryDecode(message []any, cache BinaryEncodingCache, strategy *ClientBinaryStrategy) ([]any, error) {
	if len(message) < 2 {
		return nil, fmt.Errorf("invalid message: expected headers and body, got %d elements", len(message))
	}

	headers, err := ensureStringMap(message[0])
	if err != nil {
		return nil, err
	}

	encodedBody, err := ensureAnyMap(message[1])
	if err != nil {
		return nil, err
	}

	checksums, err := extractIntSlice(headers["@bin_"])
	if err != nil || len(checksums) == 0 {
		return nil, BinaryEncoderUnavailableError{}
	}
	binaryChecksum := checksums[0]

	if encodingRaw, ok := headers["@enc_"]; ok {
		encodingMap, castErr := toStringIntMap(encodingRaw)
		if castErr != nil {
			return nil, castErr
		}
		cache.Add(binaryChecksum, encodingMap)
	}

	strategy.UpdateChecksum(binaryChecksum)
	currentChecksums := strategy.GetCurrentChecksums()
	if len(currentChecksums) == 0 {
		return nil, BinaryEncoderUnavailableError{}
	}

	encoder := cache.Get(currentChecksums[0])
	if encoder == nil {
		return nil, BinaryEncoderUnavailableError{}
	}

	var workingBody map[any]any
	if isStrictTrue(headers["@pac_"]) {
		packed, packErr := UnpackBody(encodedBody)
		if packErr != nil {
			return nil, packErr
		}
		workingBody = packed
	} else {
		workingBody = encodedBody
	}

	decodedBody, decodeErr := DecodeBody(workingBody, encoder)
	if decodeErr != nil {
		return nil, decodeErr
	}

	return []any{headers, decodedBody}, nil
}

func ensureAnyMap(value any) (map[any]any, error) {
	switch typed := value.(type) {
	case map[any]any:
		return typed, nil
	case map[string]any:
		result := make(map[any]any, len(typed))
		for key, val := range typed {
			result[key] = val
		}
		return result, nil
	case map[int]any:
		result := make(map[any]any, len(typed))
		for key, val := range typed {
			result[key] = val
		}
		return result, nil
	default:
		return nil, fmt.Errorf("expected map for encoded body, got %T", value)
	}
}

func extractIntSlice(value any) ([]int, error) {
	if value == nil {
		return []int{}, nil
	}

	switch typed := value.(type) {
	case []int:
		return append([]int{}, typed...), nil
	case []any:
		result := make([]int, 0, len(typed))
		for _, element := range typed {
			intValue, ok := toInt(element)
			if !ok {
				return nil, fmt.Errorf("invalid checksum value: %v", element)
			}
			result = append(result, intValue)
		}
		return result, nil
	case []float64:
		result := make([]int, len(typed))
		for i, element := range typed {
			result[i] = int(element)
		}
		return result, nil
	default:
		return nil, fmt.Errorf("invalid checksum list type: %T", value)
	}
}

func toStringIntMap(value any) (map[string]int, error) {
	switch typed := value.(type) {
	case map[string]int:
		return typed, nil
	case map[string]any:
		result := make(map[string]int, len(typed))
		for key, raw := range typed {
			intValue, ok := toInt(raw)
			if !ok {
				return nil, fmt.Errorf("invalid binary encoding value %v for key %s", raw, key)
			}
			result[key] = intValue
		}
		return result, nil
	case map[any]any:
		result := make(map[string]int, len(typed))
		for rawKey, raw := range typed {
			key := fmt.Sprint(rawKey)
			intValue, ok := toInt(raw)
			if !ok {
				return nil, fmt.Errorf("invalid binary encoding value %v for key %s", raw, key)
			}
			result[key] = intValue
		}
		return result, nil
	default:
		return nil, fmt.Errorf("invalid binary encoding map type: %T", value)
	}
}

func toInt(value any) (int, bool) {
	switch v := value.(type) {
	case int:
		return v, true
	case int8:
		return int(v), true
	case int16:
		return int(v), true
	case int32:
		return int(v), true
	case int64:
		return int(v), true
	case uint:
		return int(v), true
	case uint8:
		return int(v), true
	case uint16:
		return int(v), true
	case uint32:
		return int(v), true
	case uint64:
		return int(v), true
	case float32:
		return int(v), true
	case float64:
		return int(v), true
	default:
		return 0, false
	}
}
