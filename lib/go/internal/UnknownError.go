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
	cryptorand "crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"sync/atomic"
	"time"
)

var internalCaseIDFallbackCounter uint64

type telepactError struct {
	message string
	kind    string
	caseID  string
	cause   error
}

func newTelepactError(message string, kind string, cause error) *telepactError {
	return &telepactError{
		message: message,
		kind:    kind,
		caseID:  newInternalCaseID(),
		cause:   cause,
	}
}

func (e *telepactError) Error() string {
	if e == nil {
		return "<nil>"
	}
	if e.message == "" {
		if e.cause != nil {
			return e.cause.Error()
		}
		return "telepact error"
	}
	if e.cause != nil {
		return e.message + ": " + e.cause.Error()
	}
	return e.message
}

func (e *telepactError) Unwrap() error {
	if e == nil {
		return nil
	}
	return e.cause
}

func (e *telepactError) Kind() string {
	if e == nil {
		return ""
	}
	return e.kind
}

func (e *telepactError) CaseID() string {
	if e == nil {
		return ""
	}
	return e.caseID
}

func wrapUnknownError(err error, message string, kind string) *telepactError {
	var telepactErr *telepactError
	if errors.As(err, &telepactErr) {
		return telepactErr
	}
	return newTelepactError(message, kind, err)
}

func newInternalCaseID() string {
	var raw [16]byte
	if _, err := cryptorand.Read(raw[:]); err != nil {
		return fmt.Sprintf("%016x-%016x", time.Now().UnixNano(), atomic.AddUint64(&internalCaseIDFallbackCounter, 1))
	}
	raw[6] = (raw[6] & 0x0f) | 0x40
	raw[8] = (raw[8] & 0x3f) | 0x80
	encoded := hex.EncodeToString(raw[:])
	return fmt.Sprintf("%s-%s-%s-%s-%s", encoded[0:8], encoded[8:12], encoded[12:16], encoded[16:20], encoded[20:32])
}

func newUnknownErrorResponse(headers map[string]any, caseID string) ServerMessage {
	return ServerMessage{
		Headers: cloneStringAnyMap(headers),
		Body:    map[string]any{"ErrorUnknown_": map[string]any{"caseId": caseID}},
	}
}
