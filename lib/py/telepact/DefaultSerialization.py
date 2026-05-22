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
from typing import TYPE_CHECKING, cast

import msgpack  # type: ignore[import-untyped]
from msgpack import ExtType

from .Serialization import Serialization

if TYPE_CHECKING:
    from .internal.binary.BinaryEncoding import BinaryEncoding


PACKED_BYTE = 17
UNDEFINED_BYTE = 18
PACKED_EXT = ExtType(PACKED_BYTE, b'')
UNDEFINED_EXT = ExtType(UNDEFINED_BYTE, b'')
MISSING = object()


def _assign_value(holder: object, key: object, value: object) -> None:
    if type(holder) is list:
        cast(list[object], holder)[cast(int, key)] = value
    else:
        cast(dict[object, object], holder)[key] = value


def _peek_msgpack_kind(bytes_: bytes, offset: int) -> str:
    first = bytes_[offset]
    if 0x80 <= first <= 0x8f or first in (0xde, 0xdf):
        return "map"
    if 0x90 <= first <= 0x9f or first in (0xdc, 0xdd):
        return "array"
    if first in (0xc7, 0xc8, 0xc9, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8):
        return "ext"
    return "scalar"


def _is_packed_ext(value: object) -> bool:
    return type(value) is ExtType and cast(ExtType, value).code == PACKED_BYTE


def _is_undefined_ext(value: object) -> bool:
    return type(value) is ExtType and cast(ExtType, value).code == UNDEFINED_BYTE


def _pack_binary_body(packer: msgpack.Packer, body: dict[str, object],
                      binary_encoding: 'BinaryEncoding', packed: bool) -> None:
    stack: list[tuple[object, ...]] = [("value", body, tuple(), packed)]

    while stack:
        frame = stack.pop()
        frame_type = cast(str, frame[0])

        if frame_type == "raw":
            packer.pack(frame[1])
            continue

        if frame_type == "packed_row":
            row_value = cast(dict[str, object], frame[1])
            header = cast(list[object], frame[2])
            packer.pack_array_header(len(header) - 1)
            for entry in reversed(header[1:]):
                if type(entry) is list:
                    nested_header = cast(list[object], entry)
                    nested_key = cast(str, nested_header[0])
                    nested_value = row_value.get(nested_key, MISSING)
                    if nested_value is MISSING:
                        stack.append(("raw", UNDEFINED_EXT))
                    elif type(nested_value) is dict:
                        stack.append(("packed_row", nested_value, nested_header))
                    else:
                        stack.append(("value", nested_value, tuple(), False))
                else:
                    field_key = cast(str, entry)
                    field_value = row_value.get(field_key, MISSING)
                    if field_value is MISSING:
                        stack.append(("raw", UNDEFINED_EXT))
                    else:
                        stack.append(("value", field_value, tuple(), False))
            continue

        value = frame[1]
        path = cast(tuple[str, ...], frame[2])
        allow_pack_sites = cast(bool, frame[3])

        if type(value) is dict:
            value_map = cast(dict[object, object], value)
            packer.pack_map_header(len(value_map))
            for key, nested_value in reversed(list(value_map.items())):
                next_path = path + (key,) if type(key) is str else path
                stack.append(("value", nested_value, next_path, allow_pack_sites))
                stack.append(("raw", binary_encoding.encode_map[key] if type(key) is str else key))
            continue

        if type(value) is list:
            value_list = cast(list[object], value)
            pack_header = binary_encoding.pack_site_lookup.get(path) if allow_pack_sites else None
            if pack_header is not None and all(type(item) is dict for item in value_list):
                packer.pack_array_header(len(value_list) + 1)
                packer.pack(PACKED_EXT)
                for item in reversed(value_list):
                    stack.append(("packed_row", cast(dict[str, object], item), pack_header))
            else:
                packer.pack_array_header(len(value_list))
                for item in reversed(value_list):
                    stack.append(("value", item, path, False))
            continue

        packer.pack(value)


def _decode_binary_value(unpacker: msgpack.Unpacker, bytes_: bytes, binary_encoding: 'BinaryEncoding',
                         path: tuple[str, ...], allow_pack_sites: bool) -> object:
    from .internal.binary.BinaryEncodingMissing import BinaryEncodingMissing

    root_holder: list[object] = [None]
    stack: list[tuple[object, ...]] = [("value", root_holder, 0, path, allow_pack_sites)]

    while stack:
        frame = stack.pop()
        frame_type = cast(str, frame[0])

        if frame_type == "row_store":
            row_target = cast(dict[str, object], frame[1])
            header_entry = frame[2]
            temp_holder = cast(list[object], frame[3])
            value = temp_holder[0]
            if _is_undefined_ext(value):
                continue
            if type(header_entry) is list:
                row_target[cast(str, cast(list[object], header_entry)[0])] = value
            else:
                row_target[cast(str, header_entry)] = value
            continue

        if frame_type == "row":
            row_map = cast(dict[str, object], frame[1])
            header = cast(list[object], frame[2])
            index = cast(int, frame[3])
            row_size = cast(int, frame[4])
            header_entry_count = len(header) - 1

            if index >= row_size:
                continue

            if index >= header_entry_count:
                for _ in range(row_size - index):
                    unpacker.skip()
                continue

            header_entry = header[index + 1]
            temp_holder = [None]
            stack.append(("row", row_map, header, index + 1, row_size))
            stack.append(("row_store", row_map, header_entry, temp_holder))
            if type(header_entry) is list:
                stack.append(("packed_row", temp_holder, 0, cast(list[object], header_entry)))
            else:
                stack.append(("value", temp_holder, 0, tuple(), False))
            continue

        if frame_type == "packed_row":
            holder = frame[1]
            key = frame[2]
            header = cast(list[object], frame[3])
            token_kind = _peek_msgpack_kind(bytes_, unpacker.tell())
            if token_kind == "ext":
                _assign_value(holder, key, unpacker.unpack())
                continue
            if token_kind != "array":
                _assign_value(holder, key, unpacker.unpack())
                continue
            row_size = unpacker.read_array_header()
            packed_row_map: dict[str, object] = {}
            _assign_value(holder, key, packed_row_map)
            stack.append(("row", packed_row_map, header, 0, row_size))
            continue

        if frame_type == "packed_list":
            container = cast(list[object], frame[1])
            remaining = cast(int, frame[2])
            header = cast(list[object], frame[3])
            if remaining <= 0:
                continue

            index = len(container)
            container.append(None)
            stack.append(("packed_list", container, remaining - 1, header))
            stack.append(("packed_row", container, index, header))
            continue

        if frame_type == "map":
            map_container = cast(dict[str, object], frame[1])
            remaining = cast(int, frame[2])
            container_path = cast(tuple[str, ...], frame[3])
            allow_pack_sites = cast(bool, frame[4])
            if remaining <= 0:
                continue

            raw_key = unpacker.unpack()
            if type(raw_key) is int:
                try:
                    key = binary_encoding.decode_table[raw_key]
                except IndexError as e:
                    raise BinaryEncodingMissing(raw_key) from e
            else:
                key = raw_key
            next_path = container_path + (key,) if type(key) is str else container_path
            stack.append(("map", map_container, remaining - 1, container_path, allow_pack_sites))
            stack.append(("value", map_container, key, next_path, allow_pack_sites))
            continue

        if frame_type == "list":
            container = cast(list[object], frame[1])
            remaining = cast(int, frame[2])
            container_path = cast(tuple[str, ...], frame[3])
            if remaining <= 0:
                continue

            index = len(container)
            container.append(None)
            stack.append(("list", container, remaining - 1, container_path))
            stack.append(("value", container, index, container_path, False))
            continue

        holder = frame[1]
        key = frame[2]
        value_path = cast(tuple[str, ...], frame[3])
        allow_pack_sites = cast(bool, frame[4])
        token_kind = _peek_msgpack_kind(bytes_, unpacker.tell())

        if token_kind == "map":
            map_size = unpacker.read_map_header()
            value_map: dict[str, object] = {}
            _assign_value(holder, key, value_map)
            stack.append(("map", value_map, map_size, value_path, allow_pack_sites))
            continue

        if token_kind == "array":
            list_size = unpacker.read_array_header()
            pack_header = binary_encoding.pack_site_lookup.get(value_path) if allow_pack_sites else None
            if pack_header is not None and list_size > 0 and _peek_msgpack_kind(bytes_, unpacker.tell()) == "ext":
                ext_value = unpacker.unpack()
                if _is_packed_ext(ext_value):
                    packed_list: list[object] = []
                    _assign_value(holder, key, packed_list)
                    stack.append(("packed_list", packed_list, list_size - 1, pack_header))
                    continue

                prefixed_list = [ext_value]
                _assign_value(holder, key, prefixed_list)
                stack.append(("list", prefixed_list, list_size - 1, value_path))
                continue

            decoded_list: list[object] = []
            _assign_value(holder, key, decoded_list)
            stack.append(("list", decoded_list, list_size, value_path))
            continue

        _assign_value(holder, key, unpacker.unpack())

    return root_holder[0]


class DefaultSerialization(Serialization):

    def to_json(self, telepact_message: object) -> bytes:
        return json.dumps(telepact_message).encode()

    def to_msgpack(self, telepact_message: object) -> bytes:
        return msgpack.dumps(telepact_message)

    def to_binary_msgpack(self, headers: dict[str, object], body: dict[str, object],
                          binary_encoding: 'BinaryEncoding', packed: bool) -> bytes:
        packer = msgpack.Packer(autoreset=False)
        packer.pack_array_header(2)
        packer.pack(headers)
        _pack_binary_body(packer, body, binary_encoding, packed)
        return cast(bytes, packer.bytes())

    def from_json(self, bytes_: bytes) -> object:
        return json.loads(bytes_)

    def from_msgpack(self, bytes_: bytes) -> object:
        return msgpack.loads(bytes_, strict_map_key=False)

    def split_msgpack_message(self, bytes_: bytes) -> tuple[object, bytes]:
        unpacker = msgpack.Unpacker(raw=False, strict_map_key=False)
        unpacker.feed(bytes_)
        array_size = unpacker.read_array_header()
        if array_size != 2:
            raise ValueError("Telepact msgpack payload must be a two-item array")
        headers = unpacker.unpack()
        body_offset = unpacker.tell()
        return headers, bytes_[body_offset:]

    def from_binary_msgpack_body(self, bytes_: bytes, binary_encoding: 'BinaryEncoding',
                                 packed: bool) -> dict[str, object]:
        unpacker = msgpack.Unpacker(raw=False, strict_map_key=False)
        unpacker.feed(bytes_)
        value = _decode_binary_value(unpacker, bytes_, binary_encoding, tuple(), packed)
        return cast(dict[str, object], value)
