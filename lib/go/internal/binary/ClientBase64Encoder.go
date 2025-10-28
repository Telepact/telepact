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

package binary

// ClientBase64Encoder implements the Base64Encoder interface for Telepact client messages.
type ClientBase64Encoder struct{}

// NewClientBase64Encoder constructs a new ClientBase64Encoder instance.
func NewClientBase64Encoder() *ClientBase64Encoder {
	return &ClientBase64Encoder{}
}

// Decode decodes base64-encoded payload fields specified by the pseudo-JSON headers.
func (e *ClientBase64Encoder) Decode(message []any) ([]any, error) {
	if err := ClientBase64Decode(message); err != nil {
		return nil, err
	}
	return message, nil
}

// Encode traverses the message body and encodes any raw byte slices into base64 strings.
func (e *ClientBase64Encoder) Encode(message []any) ([]any, error) {
	if err := ClientBase64Encode(message); err != nil {
		return nil, err
	}
	return message, nil
}
