//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package telepact

import (
	"fmt"
	"sort"
	"strings"
)

// Message models a Telepact message with headers and a body.
type Message struct {
	Headers map[string]any
	Body    map[string]any
}

// NewMessage creates a Message with defensive copies of the provided maps.
func NewMessage(headers map[string]any, body map[string]any) Message {
	return Message{
		Headers: cloneStringMap(headers),
		Body:    cloneStringMap(body),
	}
}

// BodyTarget returns the first key in the body map, which corresponds to the target.
func (m Message) BodyTarget() (string, error) {
	keys := orderedBodyKeys(m.Body)
	if len(keys) == 0 {
		return "", NewTelepactError("message body missing target")
	}
	return keys[0], nil
}

// BodyPayload returns the payload associated with the body's target entry.
func (m Message) BodyPayload() (map[string]any, error) {
	keys := orderedBodyKeys(m.Body)
	if len(keys) == 0 {
		return nil, NewTelepactError("message body missing payload")
	}

	value := m.Body[keys[0]]
	switch typed := value.(type) {
	case map[string]any:
		return cloneStringMap(typed), nil
	case map[any]any:
		converted := make(map[string]any, len(typed))
		for k, v := range typed {
			converted[fmt.Sprint(k)] = v
		}
		return converted, nil
	default:
		return nil, NewTelepactError("message body payload is not an object")
	}
}

func cloneStringMap(source map[string]any) map[string]any {
	if source == nil {
		return nil
	}
	copy := make(map[string]any, len(source))
	for key, value := range source {
		copy[key] = value
	}
	return copy
}

func orderedBodyKeys(body map[string]any) []string {
	if len(body) == 0 {
		return nil
	}

	keys := make([]string, 0, len(body))
	for key := range body {
		keys = append(keys, key)
	}

	sort.Slice(keys, func(i, j int) bool {
		pi := bodyKeyPriority(keys[i])
		pj := bodyKeyPriority(keys[j])
		if pi != pj {
			return pi < pj
		}
		return keys[i] < keys[j]
	})

	return keys
}

func bodyKeyPriority(key string) int {
	switch {
	case strings.HasPrefix(key, "fn."):
		return 0
	case key == "Ok_":
		return 1
	case key == "Err_":
		return 2
	case !strings.HasPrefix(key, "_") && !strings.HasPrefix(key, "@"):
		return 3
	case strings.HasPrefix(key, "_"):
		return 4
	default:
		return 5
	}
}
