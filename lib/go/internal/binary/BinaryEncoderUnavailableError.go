//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// BinaryEncoderUnavailableError indicates that a binary encoder implementation is unavailable at runtime.
type BinaryEncoderUnavailableError struct{}

// Error implements the error interface.
func (BinaryEncoderUnavailableError) Error() string {
	return "binary encoder unavailable"
}
