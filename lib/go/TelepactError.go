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

package telepact

import (
	cryptorand "crypto/rand"
	"encoding/hex"
	"fmt"
	"sync/atomic"
	"time"
)

var telepactCaseIDFallbackCounter uint64

// TelepactError indicates a critical failure in Telepact processing logic.
type TelepactError struct {
	message string
	kind    string
	caseID  string
	cause   error
}

// NewTelepactError constructs a new TelepactError with the given message.
func NewTelepactError(message string) *TelepactError {
	return NewTelepactErrorWithCaseID(message, "", nil, "")
}

// NewTelepactErrorWithCause constructs a new TelepactError with a category and wrapped cause.
func NewTelepactErrorWithCause(message string, kind string, cause error) *TelepactError {
	return NewTelepactErrorWithCaseID(message, kind, cause, "")
}

// NewTelepactErrorWithCaseID constructs a new TelepactError with an explicit or generated case ID.
func NewTelepactErrorWithCaseID(message string, kind string, cause error, caseID string) *TelepactError {
	if caseID == "" {
		caseID = newTelepactCaseID()
	}
	return &TelepactError{message: message, kind: kind, caseID: caseID, cause: cause}
}

func newTelepactCaseID() string {
	var raw [16]byte
	if _, err := cryptorand.Read(raw[:]); err != nil {
		return fmt.Sprintf("%016x-%016x", time.Now().UnixNano(), atomic.AddUint64(&telepactCaseIDFallbackCounter, 1))
	}
	raw[6] = (raw[6] & 0x0f) | 0x40
	raw[8] = (raw[8] & 0x3f) | 0x80
	encoded := hex.EncodeToString(raw[:])
	return fmt.Sprintf("%s-%s-%s-%s-%s", encoded[0:8], encoded[8:12], encoded[12:16], encoded[16:20], encoded[20:32])
}

// Error implements the error interface.
func (e *TelepactError) Error() string {
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

// Unwrap exposes the wrapped cause for errors.Is/errors.As.
func (e *TelepactError) Unwrap() error {
	if e == nil {
		return nil
	}
	return e.cause
}

// Kind returns the broad diagnostic category for this error, if set.
func (e *TelepactError) Kind() string {
	if e == nil {
		return ""
	}
	return e.kind
}

// CaseID returns the server-side case identifier for this error, if set.
func (e *TelepactError) CaseID() string {
	if e == nil {
		return ""
	}
	return e.caseID
}
