//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package telepact

import "fmt"

// SerializationError indicates a failure converting between pseudo-JSON objects and serialized bytes.
type SerializationError struct {
	Message string
	Context string
	Cause   error
}

// NewSerializationError constructs a SerializationError with the provided cause.
func NewSerializationError(cause error, message string) *SerializationError {
	return &SerializationError{Message: "telepact serialization failed", Context: message, Cause: cause}
}

// Error implements the error interface.
func (e *SerializationError) Error() string {
	if e == nil {
		return "<nil>"
	}
	msg := e.Message
	if msg == "" {
		msg = "telepact serialization failed"
	}
	if e.Context != "" {
		msg = msg + " while " + e.Context
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
