//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package telepact

// Response represents a serialized payload and its associated headers.
type Response struct {
	Bytes   []byte
	Headers map[string]any
}

// NewResponse constructs a Response with defensive copies of the provided values.
func NewResponse(bytes []byte, headers map[string]any) Response {
	var clonedBytes []byte
	if bytes != nil {
		clonedBytes = make([]byte, len(bytes))
		copy(clonedBytes, bytes)
	}
	return Response{
		Bytes:   clonedBytes,
		Headers: cloneStringMap(headers),
	}
}
