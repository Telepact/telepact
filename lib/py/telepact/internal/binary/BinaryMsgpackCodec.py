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

from typing import TYPE_CHECKING

import msgpack

from .BinaryEncodingMissing import BinaryEncodingMissing

if TYPE_CHECKING:
    from .BinaryEncoding import BinaryEncoding


class _UniformDictListMismatch(Exception):
    pass


class BinaryMsgpackCodec:

    def __init__(self) -> None:
        self._packer = msgpack.Packer(autoreset=False)

    def to_binary_msgpack(self, headers: dict[str, object], body: dict[str, object],
                          binary_encoding: 'BinaryEncoding') -> bytes:
        try:
            return self._pack_message(headers, body, binary_encoding, True)
        except _UniformDictListMismatch:
            return self._pack_message(headers, body, binary_encoding, False)

    def _pack_message(self, headers: dict[str, object], body: dict[str, object],
                      binary_encoding: 'BinaryEncoding', allow_uniform_dict_lists: bool) -> bytes:
        packer = self._packer
        packer.reset()
        encode_map = binary_encoding.encode_map

        def pack_value(value: object, translate_keys: bool) -> None:
            value_type = type(value)
            if value_type is dict:
                packer.pack_map_header(len(value))
                for key, item in value.items():
                    if translate_keys and type(key) is str:
                        encoded_key = encode_map.get(key)
                        if encoded_key is not None:
                            packer.pack(encoded_key)
                        else:
                            pack_value(key, False)
                    else:
                        pack_value(key, False)
                    pack_value(item, translate_keys)
                return
            if value_type is list:
                if (allow_uniform_dict_lists
                        and translate_keys
                        and pack_uniform_dict_list(value)):
                    return
                packer.pack_array_header(len(value))
                for item in value:
                    pack_value(item, translate_keys)
                return
            packer.pack(value)

        def pack_uniform_dict_list(value: list[object]) -> bool:
            if len(value) < 16:
                return False
            first = value[0]
            if type(first) is not dict or not first:
                return False

            keys = list(first.keys())
            encoded_keys: list[int] = []
            for key in keys:
                if type(key) is not str:
                    return False
                encoded = encode_map.get(key)
                if encoded is None:
                    return False
                encoded_keys.append(encoded)

            packer.pack_array_header(len(value))
            for item in value:
                if type(item) is not dict or len(item) != len(keys):
                    raise _UniformDictListMismatch()
                for key in keys:
                    if key not in item:
                        raise _UniformDictListMismatch()
                packer.pack_map_header(len(keys))
                for index, key in enumerate(keys):
                    packer.pack(encoded_keys[index])
                    pack_value(item[key], True)
            return True

        packer.pack_array_header(2)
        pack_value(headers, False)
        pack_value(body, True)
        return packer.bytes()

    def from_msgpack_headers(self, bytes_: bytes) -> tuple[dict[object, object], int]:
        unpacker = msgpack.Unpacker(raw=False, strict_map_key=False)
        unpacker.feed(bytes_)
        if unpacker.read_array_header() != 2:
            raise ValueError("expected Telepact msgpack message array")
        headers = unpacker.unpack()
        if type(headers) is not dict:
            raise ValueError("expected Telepact msgpack headers map")
        return headers, unpacker.tell()

    def from_msgpack_body(self, bytes_: bytes, offset: int,
                          binary_encoding: 'BinaryEncoding') -> object:
        decode_table = binary_encoding.decode_table

        def decode_pairs(pairs: list[tuple[object, object]]) -> dict[str, object]:
            if pairs and type(pairs[0][0]) is int:
                decoded: dict[str, object] = {}
                try:
                    for key, value in pairs:
                        decoded[decode_table[key]] = value
                    return decoded
                except (IndexError, TypeError):
                    pass

            decoded = {}
            for key, value in pairs:
                if type(key) is str:
                    decoded_key = key
                else:
                    try:
                        decoded_key = decode_table[key]
                    except (IndexError, TypeError) as exc:
                        raise BinaryEncodingMissing(key) from exc
                decoded[decoded_key] = value
            return decoded

        unpacker = msgpack.Unpacker(raw=False, strict_map_key=False, object_pairs_hook=decode_pairs)
        unpacker.feed(memoryview(bytes_)[offset:])
        return unpacker.unpack()
