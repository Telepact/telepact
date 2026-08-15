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

// MsgpackHeaders stores decoded Telepact headers and the byte offset where the
// body begins in the original MessagePack payload.
type MsgpackHeaders struct {
	Headers    map[string]any
	BodyOffset int
}

// BinaryMsgpackSerialization exposes the optimized binary MessagePack body path.
type BinaryMsgpackSerialization interface {
	ToBinaryMsgpack(headers map[string]any, body map[string]any, encoding *BinaryEncoding) ([]byte, error)
	FromMsgpackHeaders(data []byte) (MsgpackHeaders, error)
	FromMsgpackBody(data []byte, offset int, encoding *BinaryEncoding) (map[string]any, error)
}

// MsgpackBinaryEncoder encodes and decodes binary Telepact messages directly
// from/to MessagePack bytes.
type MsgpackBinaryEncoder interface {
	EncodeToMsgpack(message []any, serializer BinaryMsgpackSerialization) ([]byte, error)
	DecodeMsgpack(data []byte, serializer BinaryMsgpackSerialization) ([]any, error)
}
