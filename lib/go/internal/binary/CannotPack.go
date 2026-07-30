//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// CannotPack indicates that a value cannot be represented in the binary encoding.
type CannotPack struct{}

// Error implements the error interface.
func (CannotPack) Error() string {
	return "cannot pack value"
}
