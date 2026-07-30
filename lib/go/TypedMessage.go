//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package telepact

// TypedMessage represents a Message with a statically typed body.
type TypedMessage[T any] struct {
	Headers map[string]any
	Body    T
}

// NewTypedMessage constructs a TypedMessage with defensive copies of the provided headers.
func NewTypedMessage[T any](headers map[string]any, body T) TypedMessage[T] {
	return TypedMessage[T]{
		Headers: cloneStringMap(headers),
		Body:    body,
	}
}
