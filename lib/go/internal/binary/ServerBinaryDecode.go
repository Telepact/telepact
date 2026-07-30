//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
