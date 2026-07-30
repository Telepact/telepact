//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package telepact

// Serialization converts between pseudo-JSON objects and serialized byte payloads.
type Serialization interface {
	ToJSON(message any) ([]byte, error)
	ToMsgpack(message any) ([]byte, error)
	FromJSON(data []byte) (any, error)
	FromMsgpack(data []byte) (any, error)
}
