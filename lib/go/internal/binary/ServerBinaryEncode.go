//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

import (
	"fmt"
	"sort"
)

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
	if len(m) == 0 {
		return ""
	}

	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys[0]
}
