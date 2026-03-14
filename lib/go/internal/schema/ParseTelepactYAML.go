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

package schema

import (
	"encoding/json"
	"fmt"
	"math"

	"gopkg.in/yaml.v3"
)

func ParseTelepactYAML(text string) (string, DocumentLocator, error) {
	var parsed any
	if err := yaml.Unmarshal([]byte(text), &parsed); err != nil {
		return "", nil, err
	}

	normalized, err := normalizeParsedYAMLValue(parsed)
	if err != nil {
		return "", nil, err
	}

	arr, ok := normalized.([]any)
	if !ok {
		return "", nil, fmt.Errorf("Telepact YAML root must be a sequence")
	}

	locator, err := CreatePathDocumentYAMLCoordinatesPseudoJSONLocator(text)
	if err != nil {
		return "", nil, err
	}

	jsonBytes, err := json.Marshal(arr)
	if err != nil {
		return "", nil, err
	}

	return string(jsonBytes), locator, nil
}

func normalizeParsedYAMLValue(value any) (any, error) {
	switch typed := value.(type) {
	case nil, bool, string, int, int8, int16, int32, int64, uint, uint8, uint16, uint32, uint64:
		return typed, nil
	case float32:
		if !isFiniteFloat64(float64(typed)) {
			return nil, fmt.Errorf("YAML values must be JSON-compatible")
		}
		return float64(typed), nil
	case float64:
		if !isFiniteFloat64(typed) {
			return nil, fmt.Errorf("YAML values must be JSON-compatible")
		}
		return typed, nil
	case []any:
		normalized := make([]any, len(typed))
		for index, child := range typed {
			value, err := normalizeParsedYAMLValue(child)
			if err != nil {
				return nil, err
			}
			normalized[index] = value
		}
		return normalized, nil
	case map[string]any:
		normalized := make(map[string]any, len(typed))
		for key, child := range typed {
			value, err := normalizeParsedYAMLValue(child)
			if err != nil {
				return nil, err
			}
			normalized[key] = value
		}
		return normalized, nil
	case map[any]any:
		normalized := make(map[string]any, len(typed))
		for key, child := range typed {
			stringKey, ok := key.(string)
			if !ok {
				return nil, fmt.Errorf("YAML values must be JSON-compatible")
			}
			value, err := normalizeParsedYAMLValue(child)
			if err != nil {
				return nil, err
			}
			normalized[stringKey] = value
		}
		return normalized, nil
	default:
		return nil, fmt.Errorf("YAML values must be JSON-compatible")
	}
}

func isFiniteFloat64(value float64) bool {
	return !math.IsNaN(value) && !math.IsInf(value, 0)
}
