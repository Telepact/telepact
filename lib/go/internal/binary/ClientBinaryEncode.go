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

// ClientBinaryEncode encodes a Telepact client message using the provided binary encoding cache and strategy.
func ClientBinaryEncode(message []any, cache BinaryEncodingCache, strategy *ClientBinaryStrategy) ([]any, error) {
	if len(message) < 2 {
		return nil, fmt.Errorf("invalid message: expected headers and body, got %d elements", len(message))
	}

	headers, err := ensureStringMap(message[0])
	if err != nil {
		return nil, err
	}

	messageBody, err := ensureStringMap(message[1])
	if err != nil {
		return nil, err
	}

	forceSendJSON := isStrictTrue(headers["_forceSendJson"])
	delete(headers, "_forceSendJson")

	checksums := strategy.GetCurrentChecksums()
	headers["@bin_"] = checksums

	if forceSendJSON {
		return nil, BinaryEncoderUnavailableError{}
	}

	if len(checksums) > 1 {
		return nil, BinaryEncoderUnavailableError{}
	}

	if len(checksums) == 0 {
		return nil, BinaryEncoderUnavailableError{}
	}

	encoding := cache.Get(checksums[0])
	if encoding == nil {
		return nil, BinaryEncoderUnavailableError{}
	}

	encodedBody, err := EncodeBody(messageBody, encoding)
	if err != nil {
		return nil, err
	}

	var finalBody map[any]any
	if isStrictTrue(headers["@pac_"]) {
		packedBody, packErr := PackBody(encodedBody)
		if packErr != nil {
			return nil, packErr
		}
		finalBody = packedBody
	} else {
		finalBody = encodedBody
	}

	return []any{headers, finalBody}, nil
}

func ensureStringMap(value any) (map[string]any, error) {
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

func isStrictTrue(value any) bool {
	boolVal, ok := value.(bool)
	return ok && boolVal
}
