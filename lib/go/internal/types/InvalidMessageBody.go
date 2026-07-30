//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// InvalidMessageBody indicates that a Telepact message body failed structural validation.
type InvalidMessageBody struct{}

// NewInvalidMessageBody constructs a new InvalidMessageBody error.
func NewInvalidMessageBody() *InvalidMessageBody {
	return &InvalidMessageBody{}
}

// Error implements the error interface.
func (e *InvalidMessageBody) Error() string {
	return "invalid message body"
}
