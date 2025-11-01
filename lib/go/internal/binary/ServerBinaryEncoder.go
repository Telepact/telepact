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

// ServerBinaryEncoder adapts ServerBinaryEncode and ServerBinaryDecode to the BinaryEncoder interface.
type ServerBinaryEncoder struct {
	binaryEncoding *BinaryEncoding
}

// NewServerBinaryEncoder constructs a ServerBinaryEncoder.
func NewServerBinaryEncoder(binaryEncoding *BinaryEncoding) *ServerBinaryEncoder {
	return &ServerBinaryEncoder{binaryEncoding: binaryEncoding}
}

// Encode encodes the provided message using the underlying binary encoding.
func (e *ServerBinaryEncoder) Encode(message []any) ([]any, error) {
	return ServerBinaryEncode(message, e.binaryEncoding)
}

// Decode decodes the provided message using the underlying binary encoding.
func (e *ServerBinaryEncoder) Decode(message []any) ([]any, error) {
	return ServerBinaryDecode(message, e.binaryEncoding)
}
