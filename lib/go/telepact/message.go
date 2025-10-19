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

import "fmt"

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
	for key := range m.Body {
		return key, nil
	}
	return "", NewTelepactError("message body missing target")
}

// BodyPayload returns the payload associated with the body's target entry.
func (m Message) BodyPayload() (map[string]any, error) {
	for _, value := range m.Body {
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
	return nil, NewTelepactError("message body missing payload")
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
