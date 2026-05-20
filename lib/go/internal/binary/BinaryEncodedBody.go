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

import (
	"encoding/json"
	"fmt"

	"github.com/telepact/telepact/lib/go/internal/msgpackjsonnumber"
	"github.com/vmihailenco/msgpack/v5"
)

type BinaryEncodedBody struct {
    Value    map[string]any
    Encoding *BinaryEncoding
}

var _ msgpack.CustomEncoder = (*BinaryEncodedBody)(nil)

func (b *BinaryEncodedBody) EncodeMsgpack(enc *msgpack.Encoder) error {
    if b == nil {
        return enc.EncodeNil()
    }
    return encodeBinaryMsgpackValue(enc, b.Value, b.Encoding)
}

func encodeBinaryMsgpackValue(enc *msgpack.Encoder, value any, encoding *BinaryEncoding) error {
    switch typed := value.(type) {
    case nil:
        return enc.EncodeNil()
    case map[string]any:
        if err := enc.EncodeMapLen(len(typed)); err != nil {
            return err
        }
        for key, item := range typed {
            mappedKey := any(key)
            if encoding != nil {
                if mapped, ok := encoding.EncodeMap[key]; ok {
                    mappedKey = mapped
                }
            }
            if err := enc.Encode(mappedKey); err != nil {
                return err
            }
            if err := encodeBinaryMsgpackValue(enc, item, encoding); err != nil {
                return err
            }
        }
        return nil
    case map[int]any:
        if err := enc.EncodeMapLen(len(typed)); err != nil {
            return err
        }
        for key, item := range typed {
            if err := enc.EncodeInt(int64(key)); err != nil {
                return err
            }
            if err := encodeBinaryMsgpackValue(enc, item, encoding); err != nil {
                return err
            }
        }
        return nil
    case map[any]any:
        if err := enc.EncodeMapLen(len(typed)); err != nil {
            return err
        }
        for rawKey, item := range typed {
            mappedKey := rawKey
            if encoding != nil {
                if mapped, ok := encoding.EncodeMap[fmt.Sprint(rawKey)]; ok {
                    mappedKey = mapped
                }
            }
            if err := enc.Encode(mappedKey); err != nil {
                return err
            }
            if err := encodeBinaryMsgpackValue(enc, item, encoding); err != nil {
                return err
            }
        }
        return nil
	case []any:
		if err := enc.EncodeArrayLen(len(typed)); err != nil {
			return err
        }
        for _, item := range typed {
            if err := encodeBinaryMsgpackValue(enc, item, encoding); err != nil {
                return err
            }
		}
		return nil
	case json.Number:
		return enc.Encode(&msgpackjsonnumber.JSONNumber{Value: string(typed)})
	default:
		return enc.Encode(value)
	}
}
