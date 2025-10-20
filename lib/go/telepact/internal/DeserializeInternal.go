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
	"fmt"

	"github.com/telepact/telepact/lib/go/telepact/internal/binary"
	"github.com/telepact/telepact/lib/go/telepact/internal/types"
)

// DeserializeInternal converts serialized bytes back into Telepact headers and body maps.
func DeserializeInternal(
	messageBytes []byte,
	serializer Serialization,
	binaryEncoder binary.BinaryEncoder,
	base64Encoder binary.Base64Encoder,
) (map[string]any, map[string]any, error) {
	if len(messageBytes) == 0 {
		return nil, nil, types.NewInvalidMessage(fmt.Errorf("empty payload"))
	}

	var (
		messageAsPseudoJSON any
		err                 error
	)

	isMsgpack := messageBytes[0] == 0x92

	if isMsgpack {
		messageAsPseudoJSON, err = serializer.FromMsgpack(messageBytes)
	} else {
		messageAsPseudoJSON, err = serializer.FromJSON(messageBytes)
	}
	if err != nil {
		return nil, nil, types.NewInvalidMessage(err)
	}

	messageList, ok := messageAsPseudoJSON.([]any)
	if !ok || len(messageList) != 2 {
		return nil, nil, types.NewInvalidMessage(nil)
	}

	var finalList []any
	if isMsgpack {
		finalList, err = binaryEncoder.Decode(messageList)
	} else {
		finalList, err = base64Encoder.Decode(messageList)
	}
	if err != nil {
		return nil, nil, types.NewInvalidMessage(err)
	}

	if len(finalList) != 2 {
		return nil, nil, types.NewInvalidMessage(nil)
	}

	headers, ok := toStringMap(finalList[0])
	if !ok {
		return nil, nil, types.NewInvalidMessage(nil)
	}

	body, ok := toStringMap(finalList[1])
	if !ok {
		return nil, nil, types.NewInvalidMessage(nil)
	}

	if len(body) != 1 {
		return nil, nil, types.NewInvalidMessageBody()
	}

	for key, value := range body {
		converted, ok := toStringMap(value)
		if !ok {
			return nil, nil, types.NewInvalidMessageBody()
		}
		body[key] = converted
	}

	return headers, body, nil
}

func toStringMap(value any) (map[string]any, bool) {
	switch typed := value.(type) {
	case map[string]any:
		return typed, true
	case map[any]any:
		converted := make(map[string]any, len(typed))
		for k, v := range typed {
			converted[fmt.Sprint(k)] = v
		}
		return converted, true
	default:
		return nil, false
	}
}
