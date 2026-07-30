//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// BinaryEncoder defines methods for encoding and decoding pseudo-JSON Telepact messages into a binary representation.
type BinaryEncoder interface {
	Encode(message []any) ([]any, error)
	Decode(message []any) ([]any, error)
}
