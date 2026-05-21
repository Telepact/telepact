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


def _pack_msgpack_value(
    packer: msgpack.Packer,
    value: object,
    binary_encoding: object | None = None,
) -> None:
    if type(value) is BinaryEncodedBody:
        _pack_msgpack_value(packer, value.value, value.binary_encoding)
        return
    if type(value) is dict:
        _pack_binary_map(packer, value, binary_encoding)
        return
    if type(value) is list:
        packer.pack_array_header(len(value))
        for item in value:
            _pack_msgpack_value(packer, item, binary_encoding)
        return
    try:
        packer.pack(value)
    except TypeError as e:
        raise TypeError(
            f"Cannot serialize object of type {type(value).__name__}"
        ) from e


def _pack_binary_map(
    packer: msgpack.Packer,
    value: dict[object, object],
    binary_encoding: object | None,
) -> None:
    encode_map = binary_encoding.encode_map if binary_encoding is not None else {}

    packer.pack_map_header(len(value))
    for key, item in value.items():
        packer.pack(encode_map.get(key, key))
        _pack_msgpack_value(packer, item, binary_encoding)


class DefaultSerialization(Serialization):

    def to_json(self, telepact_message: object) -> bytes:
        return json.dumps(telepact_message).encode()

    def to_msgpack(self, telepact_message: object) -> bytes:
        packer = msgpack.Packer(autoreset=False)
        _pack_msgpack_value(packer, telepact_message)
        return packer.bytes()

    def from_json(self, bytes_: bytes) -> object:
        return json.loads(bytes_)

    def from_msgpack(self, bytes_: bytes) -> object:
        return msgpack.loads(bytes_, strict_map_key=False)
