//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

import "fmt"

// InvalidMessage indicates that a serialized Telepact message failed validation.
type InvalidMessage struct {
	Cause error
}

// NewInvalidMessage constructs an InvalidMessage with the provided cause.
func NewInvalidMessage(cause error) *InvalidMessage {
	return &InvalidMessage{Cause: cause}
}

// Error implements the error interface.
func (e *InvalidMessage) Error() string {
	if e == nil {
		return "<nil>"
	}
	if e.Cause != nil {
		return fmt.Sprintf("invalid message: %v", e.Cause)
	}
	return "invalid message"
}

// Unwrap exposes the underlying cause for errors.Is/As.
func (e *InvalidMessage) Unwrap() error {
	if e == nil {
		return nil
	}
	return e.Cause
}
