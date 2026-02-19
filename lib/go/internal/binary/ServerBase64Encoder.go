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

// ServerBase64Encoder implements Base64Encoder for server-side processing.
type ServerBase64Encoder struct{}

// NewServerBase64Encoder constructs a ServerBase64Encoder instance.
func NewServerBase64Encoder() *ServerBase64Encoder {
	return &ServerBase64Encoder{}
}

// Decode is a no-op on the server side; decoding occurs after validation.
func (e *ServerBase64Encoder) Decode(message []any) ([]any, error) {
	return message, nil
}

// Encode applies server-side base64 encoding to the provided message.
func (e *ServerBase64Encoder) Encode(message []any) ([]any, error) {
	if err := ServerBase64Encode(message); err != nil {
		return nil, err
	}
	return message, nil
}
