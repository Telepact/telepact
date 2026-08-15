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

import msgpack
import json

from .Serialization import Serialization
from .internal.binary.BinaryMsgpackCodec import BinaryMsgpackCodec
from .internal.binary.BinaryMsgpackSerialization import BinaryMsgpackSerialization


class DefaultSerialization(Serialization, BinaryMsgpackSerialization):

    def __init__(self) -> None:
        self._msgpack_packer = msgpack.Packer(autoreset=True)
        self._binary_msgpack = BinaryMsgpackCodec()

    def to_json(self, telepact_message: object) -> bytes:
        return json.dumps(telepact_message).encode()

    def to_msgpack(self, telepact_message: object) -> bytes:
        return self._msgpack_packer.pack(telepact_message)

    def to_binary_msgpack(self, headers: dict[str, object], body: dict[str, object], binary_encoding: object) -> bytes:
        return self._binary_msgpack.to_binary_msgpack(headers, body, binary_encoding)

    def from_json(self, bytes_: bytes) -> object:
        return json.loads(bytes_)

    def from_msgpack(self, bytes_: bytes) -> object:
        return msgpack.loads(bytes_, strict_map_key=False)

    def from_msgpack_headers(self, bytes_: bytes) -> tuple[dict[object, object], int]:
        return self._binary_msgpack.from_msgpack_headers(bytes_)

    def from_msgpack_body(self, bytes_: bytes, offset: int, binary_encoding: object) -> object:
        return self._binary_msgpack.from_msgpack_body(bytes_, offset, binary_encoding)
