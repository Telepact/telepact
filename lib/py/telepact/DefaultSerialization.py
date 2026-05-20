#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

import json
import msgpack

from .Serialization import Serialization
from .internal.binary.BinaryEncodedBody import BinaryEncodedBody


def _encode_binary_value(value: object, binary_encoding: object) -> object:
    encode_map = binary_encoding.encode_map

    if type(value) is dict:
        return {
            encode_map.get(key, key): _encode_binary_value(item, binary_encoding)
            for key, item in value.items()
        }
    if type(value) is list:
        return [_encode_binary_value(item, binary_encoding) for item in value]
    return value


class DefaultSerialization(Serialization):

    def to_json(self, telepact_message: object) -> bytes:
        return json.dumps(telepact_message).encode()

    def to_msgpack(self, telepact_message: object) -> bytes:
        def default(value: object) -> object:
            if type(value) is BinaryEncodedBody:
                return _encode_binary_value(value.value, value.binary_encoding)
            raise TypeError(f"Cannot serialize object of type {type(value).__name__}")

        return msgpack.dumps(telepact_message, default=default)

    def from_json(self, bytes_: bytes) -> object:
        return json.loads(bytes_)

    def from_msgpack(self, bytes_: bytes) -> object:
        return msgpack.loads(bytes_, strict_map_key=False)
