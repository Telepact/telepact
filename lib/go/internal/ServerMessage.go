//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package internal

// ServerMessage models the headers and body exchanged with Telepact servers.
type ServerMessage struct {
	Headers map[string]any
	Body    map[string]any
}

func cloneStringAnyMap(source map[string]any) map[string]any {
	if source == nil {
		return make(map[string]any)
	}
	copy := make(map[string]any, len(source))
	for key, value := range source {
		copy[key] = value
	}
	return copy
}
