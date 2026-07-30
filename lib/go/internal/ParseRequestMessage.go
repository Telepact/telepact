//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package internal

import (
	"errors"
	"fmt"

	"github.com/telepact/telepact/lib/go/internal/binary"
	"github.com/telepact/telepact/lib/go/internal/types"
)

func ParseRequestMessage(
	requestMessageBytes []byte,
	deserialize func([]byte) (ServerMessage, error),
	schema SchemaAccessor,
	onError func(error),
) (ServerMessage, error) {
	_ = schema

	message, err := deserialize(requestMessageBytes)
	if err == nil {
		return message, nil
	}

	invokeOnError(onError, fmt.Errorf("telepact request parsing failed while decoding the incoming message: %w", err))

	reason := "ExpectedJsonArrayOfTwoObjects"

	var unavailableErr binary.BinaryEncoderUnavailableError
	if errors.As(err, &unavailableErr) {
		reason = "IncompatibleBinaryEncoding"
	} else {
		var missingErr *binary.BinaryEncodingMissing
		if errors.As(err, &missingErr) {
			reason = "BinaryDecodeFailure"
		} else {
			var invalidMessageErr *types.InvalidMessage
			if errors.As(err, &invalidMessageErr) {
				reason = "ExpectedJsonArrayOfTwoObjects"
			} else {
				var invalidBodyErr *types.InvalidMessageBody
				if errors.As(err, &invalidBodyErr) {
					reason = "ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject"
				}
			}
		}
	}

	parseHeaders := map[string]any{
		"_parseFailures": []any{map[string]any{reason: map[string]any{}}},
	}
	parseBody := map[string]any{
		"_unknown": map[string]any{},
	}

	return ServerMessage{Headers: parseHeaders, Body: parseBody}, nil
}
