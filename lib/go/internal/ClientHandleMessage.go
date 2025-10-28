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
	"context"
	"time"
)

// ClientMessage represents a Telepact message as seen by the internal client handler.
type ClientMessage struct {
	Headers map[string]any
	Body    map[string]any
}

// NewClientMessage constructs a ClientMessage instance.
func NewClientMessage(headers map[string]any, body map[string]any) *ClientMessage {
	return &ClientMessage{
		Headers: headers,
		Body:    body,
	}
}

// ClientHandleMessageAdapter delegates request processing to the transport adapter.
type ClientHandleMessageAdapter func(ctx context.Context, request *ClientMessage) (*ClientMessage, error)

// ClientHandleMessage applies Telepact client defaults before invoking the transport adapter.
func ClientHandleMessage(
	ctx context.Context,
	request *ClientMessage,
	adapter ClientHandleMessageAdapter,
	timeoutMSDefault int,
	useBinaryDefault bool,
	alwaysSendJSON bool,
) (*ClientMessage, error) {
	if ctx == nil {
		ctx = context.Background()
	}

	headers := ensureHeaders(request)
	if _, ok := headers["@time_"]; !ok {
		headers["@time_"] = timeoutMSDefault
	}

	if useBinaryDefault {
		headers["@binary_"] = true
	}

	if isBinary(headers) && alwaysSendJSON {
		headers["_forceSendJson"] = true
	}

	timeout := timeoutFromHeader(headers["@time_"], timeoutMSDefault)
	response, err := executeWithTimeout(ctx, timeout, adapter, request)
	if err != nil {
		return nil, err
	}

	if isIncompatibleBinaryEncoding(response.Body) {
		headers["@binary_"] = true
		headers["_forceSendJson"] = true

		return executeWithTimeout(ctx, timeout, adapter, request)
	}

	return response, nil
}

func ensureHeaders(message *ClientMessage) map[string]any {
	if message.Headers == nil {
		message.Headers = make(map[string]any)
	}
	return message.Headers
}

func isBinary(headers map[string]any) bool {
	flag, ok := headers["@binary_"].(bool)
	return ok && flag
}

func timeoutFromHeader(value any, defaultMS int) time.Duration {
	switch v := value.(type) {
	case int:
		if v > 0 {
			return time.Duration(v) * time.Millisecond
		}
	case int32:
		if v > 0 {
			return time.Duration(v) * time.Millisecond
		}
	case int64:
		if v > 0 {
			return time.Duration(v) * time.Millisecond
		}
	case float32:
		if v > 0 {
			return time.Duration(v) * time.Millisecond
		}
	case float64:
		if v > 0 {
			return time.Duration(v) * time.Millisecond
		}
	case uint:
		if v > 0 {
			return time.Duration(v) * time.Millisecond
		}
	case uint32:
		if v > 0 {
			return time.Duration(v) * time.Millisecond
		}
	case uint64:
		if v > 0 {
			return time.Duration(v) * time.Millisecond
		}
	}
	return time.Duration(defaultMS) * time.Millisecond
}

func executeWithTimeout(
	ctx context.Context,
	timeout time.Duration,
	adapter ClientHandleMessageAdapter,
	request *ClientMessage,
) (*ClientMessage, error) {
	ctxWithTimeout, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	type adapterResult struct {
		response *ClientMessage
		err      error
	}

	resultCh := make(chan adapterResult, 1)
	go func() {
		resp, err := adapter(ctxWithTimeout, request)
		resultCh <- adapterResult{response: resp, err: err}
	}()

	select {
	case <-ctxWithTimeout.Done():
		return nil, ctxWithTimeout.Err()
	case result := <-resultCh:
		return result.response, result.err
	}
}

func isIncompatibleBinaryEncoding(body map[string]any) bool {
	if body == nil {
		return false
	}

	payload, ok := body["ErrorParseFailure_"].(map[string]any)
	if !ok {
		return false
	}

	reasonsRaw, ok := payload["reasons"]
	if !ok {
		return false
	}

	reasons, ok := reasonsRaw.([]any)
	if !ok || len(reasons) != 1 {
		return false
	}

	reason, ok := reasons[0].(map[string]any)
	if !ok {
		return false
	}

	value, ok := reason["IncompatibleBinaryEncoding"]
	if !ok {
		return false
	}

	switch typed := value.(type) {
	case map[string]any:
		return len(typed) == 0
	case map[any]any:
		return len(typed) == 0
	case nil:
		return true
	default:
		return false
	}
}
