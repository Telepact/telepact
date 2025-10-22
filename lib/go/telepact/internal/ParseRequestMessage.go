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

package internal

import (
	"errors"

	"github.com/telepact/telepact/lib/go/telepact/internal/binary"
	"github.com/telepact/telepact/lib/go/telepact/internal/types"
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

	invokeOnError(onError, err)

	reason := "ExpectedJsonArrayOfTwoObjects"

	var unavailableErr *binary.BinaryEncoderUnavailableError
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
