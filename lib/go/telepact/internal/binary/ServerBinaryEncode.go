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

// ServerBinaryEncode encodes a pseudo-JSON response message into its binary representation for the client.
func ServerBinaryEncode(message []any, binaryEncoding *BinaryEncoding) ([]any, error) {
	if binaryEncoding == nil {
		return nil, BinaryEncoderUnavailableError{}
	}
	if len(message) != 2 {
		return nil, fmt.Errorf("invalid message: expected two elements, got %d", len(message))
	}

	headers, err := ensureStringMap(message[0])
	if err != nil {
		return nil, err
	}

	messageBody, err := ensureStringMap(message[1])
	if err != nil {
		return nil, err
	}

	clientKnownRaw, hasClientKnown := headers["@clientKnownBinaryChecksums_"]
	if hasClientKnown {
		delete(headers, "@clientKnownBinaryChecksums_")
	}

	clientKnown, err := extractIntSlice(clientKnownRaw)
	if err != nil {
		return nil, err
	}

	resultTag := firstKey(messageBody)
	if resultTag != "Ok_" {
		return nil, BinaryEncoderUnavailableError{}
	}

	checksumKnown := false
	for _, checksum := range clientKnown {
		if binaryEncoding != nil && checksum == binaryEncoding.Checksum {
			checksumKnown = true
			break
		}
	}

	if !checksumKnown {
		encodeMapCopy := make(map[string]int, len(binaryEncoding.EncodeMap))
		for key, value := range binaryEncoding.EncodeMap {
			encodeMapCopy[key] = value
		}
		headers["@enc_"] = encodeMapCopy
	}

	headers["@bin_"] = []int{binaryEncoding.Checksum}

	encodedBody, err := EncodeBody(messageBody, binaryEncoding)
	if err != nil {
		return nil, err
	}

	finalEncodedBody := encodedBody
	if isStrictTrue(headers["@pac_"]) {
		packedBody, err := PackBody(encodedBody)
		if err != nil {
			return nil, err
		}
		finalEncodedBody = packedBody
	}

	return []any{headers, finalEncodedBody}, nil
}

func firstKey(m map[string]any) string {
	for key := range m {
		return key
	}
	return ""
}
