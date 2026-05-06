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

// ServerBinaryDecode transforms an encoded message into its pseudo-JSON representation.
func ServerBinaryDecode(message []any, binaryEncoding *BinaryEncoding) ([]any, error) {
	if len(message) != 2 {
		return nil, fmt.Errorf("invalid message: expected two elements, got %d", len(message))
	}

	headers, err := ensureStringMap(message[0])
	if err != nil {
		return nil, err
	}

	encodedBody, err := ensureAnyMap(message[1])
	if err != nil {
		return nil, err
	}

	clientChecksums, err := extractIntSlice(headers["@bin_"])
	if err != nil {
		return nil, err
	}
	if len(clientChecksums) == 0 {
		return nil, BinaryEncoderUnavailableError{}
	}

	checksumUsed := clientChecksums[0]
	if binaryEncoding == nil || checksumUsed != binaryEncoding.Checksum {
		return nil, BinaryEncoderUnavailableError{}
	}

	finalEncodedBody := encodedBody
	if isStrictTrue(headers["@pac_"]) {
		unpacked, err := UnpackBody(encodedBody)
		if err != nil {
			return nil, err
		}
		finalEncodedBody = unpacked
	}

	messageBody, err := DecodeBody(finalEncodedBody, binaryEncoding)
	if err != nil {
		return nil, err
	}

	return []any{headers, messageBody}, nil
}
