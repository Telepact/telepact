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

import "fmt"

// SerializationError indicates a failure converting between pseudo-JSON objects and serialized bytes.
type SerializationError struct {
	Message string
	Cause   error
}

// NewSerializationError constructs a SerializationError with the provided cause.
func NewSerializationError(cause error, message string) *SerializationError {
	return &SerializationError{Message: message, Cause: cause}
}

// Error implements the error interface.
func (e *SerializationError) Error() string {
	if e == nil {
		return "<nil>"
	}
	msg := e.Message
	if msg == "" {
		msg = "serialization error"
	}
	if e.Cause != nil {
		return fmt.Sprintf("%s: %v", msg, e.Cause)
	}
	return msg
}

// Unwrap exposes the wrapped cause for errors.Is/As.
func (e *SerializationError) Unwrap() error {
	if e == nil {
		return nil
	}
	return e.Cause
}
