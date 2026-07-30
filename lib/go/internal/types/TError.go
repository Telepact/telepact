//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package types

// TError represents an error type wrapping an underlying union.
type TError struct {
	Name   string
	Errors *TUnion
}

// NewTError constructs a TError instance.
func NewTError(name string, errors *TUnion) *TError {
	return &TError{Name: name, Errors: errors}
}
