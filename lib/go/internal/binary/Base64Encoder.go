//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

// Base64Encoder defines methods for encoding and decoding pseudo-JSON Telepact messages via Base64.
type Base64Encoder interface {
	Decode(message []any) ([]any, error)
	Encode(message []any) ([]any, error)
}
