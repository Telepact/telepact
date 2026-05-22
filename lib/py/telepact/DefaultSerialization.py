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
from typing import TYPE_CHECKING, Any, cast

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

FRAME_RAW = 0
FRAME_VALUE = 1
FRAME_PACKED_ROW = 2
FRAME_ROW_STORE = 3
FRAME_ROW = 4
FRAME_PACKED_LIST = 5
FRAME_MAP = 6
FRAME_LIST = 7


def _encode_packed_row_tree(row_value: dict[object, object], header: list[object],
                            encode_map: dict[str, int],
                            pack_site_lookup: dict[tuple[str, ...], list[object]]) -> list[object]:
    row: list[object] = []
    row_append = row.append

    for entry in header[1:]:
        if type(entry) is list:
            nested_header = cast(list[object], entry)
            nested_key = nested_header[0]
            nested_value = row_value.get(nested_key, MISSING)
            if nested_value is MISSING:
                row_append(UNDEFINED_EXT)
            elif type(nested_value) is dict:
                row_append(_encode_packed_row_tree(
                    cast(dict[object, object], nested_value), nested_header, encode_map, pack_site_lookup))
            else:
                row_append(_encode_binary_value_tree(
                    nested_value, tuple(), False, encode_map, pack_site_lookup))
        else:
            field_value = row_value.get(entry, MISSING)
            if field_value is MISSING:
                row_append(UNDEFINED_EXT)
            else:
                row_append(_encode_binary_value_tree(
                    field_value, tuple(), False, encode_map, pack_site_lookup))

    return row


def _encode_binary_value_tree(value: object, path: tuple[str, ...], allow_pack_sites: bool,
                              encode_map: dict[str, int],
                              pack_site_lookup: dict[tuple[str, ...], list[object]]) -> object:
    if type(value) is dict:
        value_map = cast(dict[object, object], value)
        encoded_map: dict[object, object] = {}
        encoded_map_set = encoded_map.__setitem__

        for key, nested_value in value_map.items():
            if type(key) is str:
                encoded_key: object = encode_map[key]
                next_path = path + (key,) if allow_pack_sites else path
            else:
                encoded_key = key
                next_path = path

            encoded_map_set(
                encoded_key,
                _encode_binary_value_tree(nested_value, next_path, allow_pack_sites, encode_map, pack_site_lookup),
            )

        return encoded_map

    if type(value) is list:
        value_list = cast(list[object], value)
        pack_header = pack_site_lookup.get(path) if allow_pack_sites else None
        if pack_header is not None and all(type(item) is dict for item in value_list):
            return [
                PACKED_EXT,
                *[
                    _encode_packed_row_tree(cast(dict[object, object], item), pack_header,
                                            encode_map, pack_site_lookup)
                    for item in value_list
                ],
            ]

        return [
            _encode_binary_value_tree(item, path, False, encode_map, pack_site_lookup)
            for item in value_list
        ]

    return value


def _decode_packed_row_tree(row_value: list[object], header: list[object], decode_table: list[str],
                            pack_site_lookup: dict[tuple[str, ...], list[object]]) -> dict[str, object]:
    row_map: dict[str, object] = {}
    row_map_set = row_map.__setitem__
    header_entry_count = len(header) - 1

    for index in range(min(len(row_value), header_entry_count)):
        value = row_value[index]
        if type(value) is ExtType and value.code == UNDEFINED_BYTE:
            continue

        header_entry = header[index + 1]
        if type(header_entry) is list:
            nested_header = cast(list[object], header_entry)
            row_map_set(
                cast(str, nested_header[0]),
                _decode_binary_value_tree(value, tuple(), False, decode_table, pack_site_lookup)
                if type(value) is not list
                else _decode_packed_row_tree(cast(list[object], value), nested_header,
                                             decode_table, pack_site_lookup),
            )
        else:
            row_map_set(
                cast(str, header_entry),
                _decode_binary_value_tree(value, tuple(), False, decode_table, pack_site_lookup),
            )

    return row_map


def _decode_binary_value_tree(value: object, path: tuple[str, ...], allow_pack_sites: bool,
                              decode_table: list[str],
                              pack_site_lookup: dict[tuple[str, ...], list[object]]) -> object:
    from .internal.binary.BinaryEncodingMissing import BinaryEncodingMissing

    if type(value) is dict:
        value_map = cast(dict[object, object], value)
        decoded_map: dict[object, object] = {}
        decoded_map_set = decoded_map.__setitem__

        for raw_key, nested_value in value_map.items():
            if type(raw_key) is int:
                try:
                    key: object = decode_table[raw_key]
                except IndexError as e:
                    raise BinaryEncodingMissing(raw_key) from e
            else:
                key = raw_key

            next_path = path + (key,) if allow_pack_sites and type(key) is str else path
            decoded_map_set(
                key,
                _decode_binary_value_tree(nested_value, next_path, allow_pack_sites,
                                          decode_table, pack_site_lookup),
            )

        return decoded_map

    if type(value) is list:
        value_list = cast(list[object], value)
        pack_header = pack_site_lookup.get(path) if allow_pack_sites else None
        if pack_header is not None and value_list and type(value_list[0]) is ExtType:
            first_item = cast(ExtType, value_list[0])
            if first_item.code == PACKED_BYTE:
                return [
                    _decode_binary_value_tree(item, tuple(), False, decode_table, pack_site_lookup)
                    if type(item) is not list
                    else _decode_packed_row_tree(cast(list[object], item), pack_header,
                                                 decode_table, pack_site_lookup)
                    for item in value_list[1:]
                ]

        return [
            _decode_binary_value_tree(item, path, False, decode_table, pack_site_lookup)
            for item in value_list
        ]

    return value


def _decode_binary_keys_only(value: object, decode_table: list[str]) -> object:
    from .internal.binary.BinaryEncodingMissing import BinaryEncodingMissing

    def decode_key(raw_key: object) -> str:
        try:
            if type(raw_key) is not int:
                raise TypeError()
            return decode_table[raw_key]
        except (IndexError, TypeError) as exc:
            raise BinaryEncodingMissing(raw_key) from exc

    def decode_value(decoded_value: object) -> object:
        value_type = type(decoded_value)

        if value_type is dict:
            value_map = cast(dict[object, object], decoded_value)
            result: dict[str, object] = {}
            result_set = result.__setitem__
            for raw_key, nested_value in value_map.items():
                result_set(
                    cast(str, raw_key) if type(raw_key) is str else decode_key(raw_key),
                    decode_value(nested_value),
                )
            return result

        if value_type is list:
            return [decode_value(item) for item in cast(list[object], decoded_value)]

        return decoded_value

    return decode_value(value)


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
    stack: list[tuple[Any, ...]] = [(FRAME_VALUE, body, tuple(), packed)]
    encode_map = binary_encoding.encode_map
    pack_site_lookup = binary_encoding.pack_site_lookup
    pack = packer.pack
    pack_map_header = packer.pack_map_header
    pack_array_header = packer.pack_array_header

    while stack:
        frame = stack.pop()
        frame_type = frame[0]

        if frame_type == FRAME_RAW:
            pack(frame[1])
            continue

        if frame_type == FRAME_PACKED_ROW:
            row_value = frame[1]
            header = frame[2]
            pack_array_header(len(header) - 1)
            for entry in reversed(header[1:]):
                if type(entry) is list:
                    nested_header = entry
                    nested_key = nested_header[0]
                    nested_value = row_value.get(nested_key, MISSING)
                    if nested_value is MISSING:
                        stack.append((FRAME_RAW, UNDEFINED_EXT))
                    elif type(nested_value) is dict:
                        stack.append((FRAME_PACKED_ROW, nested_value, nested_header))
                    else:
                        stack.append((FRAME_VALUE, nested_value, tuple(), False))
                else:
                    field_key = entry
                    field_value = row_value.get(field_key, MISSING)
                    if field_value is MISSING:
                        stack.append((FRAME_RAW, UNDEFINED_EXT))
                    else:
                        stack.append((FRAME_VALUE, field_value, tuple(), False))
            continue

        value = frame[1]
        path = frame[2]
        allow_pack_sites = frame[3]

        if type(value) is dict:
            value_map = value
            pack_map_header(len(value_map))
            for key, nested_value in reversed(list(value_map.items())):
                next_path = path + (key,) if type(key) is str else path
                stack.append((FRAME_VALUE, nested_value, next_path, allow_pack_sites))
                stack.append((FRAME_RAW, encode_map[key] if type(key) is str else key))
            continue

        if type(value) is list:
            value_list = value
            pack_header = pack_site_lookup.get(path) if allow_pack_sites else None
            if pack_header is not None and all(type(item) is dict for item in value_list):
                pack_array_header(len(value_list) + 1)
                pack(PACKED_EXT)
                for item in reversed(value_list):
                    stack.append((FRAME_PACKED_ROW, item, pack_header))
            else:
                pack_array_header(len(value_list))
                for item in reversed(value_list):
                    stack.append((FRAME_VALUE, item, path, False))
            continue

        pack(value)


def _decode_binary_value(unpacker: msgpack.Unpacker, bytes_: bytes, binary_encoding: 'BinaryEncoding',
                         path: tuple[str, ...], allow_pack_sites: bool) -> object:
    from .internal.binary.BinaryEncodingMissing import BinaryEncodingMissing

    root_holder: list[object] = [None]
    stack: list[tuple[Any, ...]] = [(FRAME_VALUE, root_holder, 0, path, allow_pack_sites)]
    decode_table = binary_encoding.decode_table
    pack_site_lookup = binary_encoding.pack_site_lookup
    unpack = unpacker.unpack
    unpack_skip = unpacker.skip
    read_array_header = unpacker.read_array_header
    read_map_header = unpacker.read_map_header
    tell = unpacker.tell

    while stack:
        frame = stack.pop()
        frame_type = frame[0]

        if frame_type == FRAME_ROW_STORE:
            row_target = frame[1]
            header_entry = frame[2]
            temp_holder = frame[3]
            value = temp_holder[0]
            if type(value) is ExtType and value.code == UNDEFINED_BYTE:
                continue
            if type(header_entry) is list:
                row_target[header_entry[0]] = value
            else:
                row_target[header_entry] = value
            continue

        if frame_type == FRAME_ROW:
            row_map = frame[1]
            header = frame[2]
            index = frame[3]
            row_size = frame[4]
            header_entry_count = len(header) - 1

            if index >= row_size:
                continue

            if index >= header_entry_count:
                for _ in range(row_size - index):
                    unpack_skip()
                continue

            header_entry = header[index + 1]
            temp_holder = [None]
            stack.append((FRAME_ROW, row_map, header, index + 1, row_size))
            stack.append((FRAME_ROW_STORE, row_map, header_entry, temp_holder))
            if type(header_entry) is list:
                stack.append((FRAME_PACKED_ROW, temp_holder, 0, header_entry))
            else:
                stack.append((FRAME_VALUE, temp_holder, 0, tuple(), False))
            continue

        if frame_type == FRAME_PACKED_ROW:
            holder = frame[1]
            key = frame[2]
            header = frame[3]
            token_kind = _peek_msgpack_kind(bytes_, tell())
            if token_kind == "ext":
                if type(holder) is list:
                    holder[key] = unpack()
                else:
                    holder[key] = unpack()
                continue
            if token_kind != "array":
                if type(holder) is list:
                    holder[key] = unpack()
                else:
                    holder[key] = unpack()
                continue
            row_size = read_array_header()
            packed_row_map: dict[str, object] = {}
            if type(holder) is list:
                holder[key] = packed_row_map
            else:
                holder[key] = packed_row_map
            stack.append((FRAME_ROW, packed_row_map, header, 0, row_size))
            continue

        if frame_type == FRAME_PACKED_LIST:
            container = frame[1]
            remaining = frame[2]
            header = frame[3]
            if remaining <= 0:
                continue

            index = len(container)
            container.append(None)
            stack.append((FRAME_PACKED_LIST, container, remaining - 1, header))
            stack.append((FRAME_PACKED_ROW, container, index, header))
            continue

        if frame_type == FRAME_MAP:
            map_container = frame[1]
            remaining = frame[2]
            container_path = frame[3]
            allow_pack_sites = frame[4]
            if remaining <= 0:
                continue

            raw_key = unpack()
            if type(raw_key) is int:
                try:
                    key = decode_table[raw_key]
                except IndexError as e:
                    raise BinaryEncodingMissing(raw_key) from e
            else:
                key = raw_key
            next_path = container_path + (key,) if type(key) is str else container_path
            stack.append((FRAME_MAP, map_container, remaining - 1, container_path, allow_pack_sites))
            stack.append((FRAME_VALUE, map_container, key, next_path, allow_pack_sites))
            continue

        if frame_type == FRAME_LIST:
            container = frame[1]
            remaining = frame[2]
            container_path = frame[3]
            if remaining <= 0:
                continue

            index = len(container)
            container.append(None)
            stack.append((FRAME_LIST, container, remaining - 1, container_path))
            stack.append((FRAME_VALUE, container, index, container_path, False))
            continue

        holder = frame[1]
        key = frame[2]
        value_path = frame[3]
        allow_pack_sites = frame[4]
        token_kind = _peek_msgpack_kind(bytes_, tell())

        if token_kind == "map":
            map_size = read_map_header()
            value_map: dict[str, object] = {}
            if type(holder) is list:
                holder[key] = value_map
            else:
                holder[key] = value_map
            stack.append((FRAME_MAP, value_map, map_size, value_path, allow_pack_sites))
            continue

        if token_kind == "array":
            list_size = read_array_header()
            pack_header = pack_site_lookup.get(value_path) if allow_pack_sites else None
            if pack_header is not None and list_size > 0 and _peek_msgpack_kind(bytes_, tell()) == "ext":
                ext_value = unpack()
                if type(ext_value) is ExtType and ext_value.code == PACKED_BYTE:
                    packed_list: list[object] = []
                    if type(holder) is list:
                        holder[key] = packed_list
                    else:
                        holder[key] = packed_list
                    stack.append((FRAME_PACKED_LIST, packed_list, list_size - 1, pack_header))
                    continue

                prefixed_list = [ext_value]
                if type(holder) is list:
                    holder[key] = prefixed_list
                else:
                    holder[key] = prefixed_list
                stack.append((FRAME_LIST, prefixed_list, list_size - 1, value_path))
                continue

            decoded_list: list[object] = []
            if type(holder) is list:
                holder[key] = decoded_list
            else:
                holder[key] = decoded_list
            stack.append((FRAME_LIST, decoded_list, list_size, value_path))
            continue

        if type(holder) is list:
            holder[key] = unpack()
        else:
            holder[key] = unpack()

    return root_holder[0]


class DefaultSerialization(Serialization):

    def to_json(self, telepact_message: object) -> bytes:
        return json.dumps(telepact_message).encode()

    def to_msgpack(self, telepact_message: object) -> bytes:
        return msgpack.dumps(telepact_message)

    def to_binary_msgpack(self, headers: dict[str, object], body: dict[str, object],
                          binary_encoding: 'BinaryEncoding', packed: bool) -> bytes:
        encoded_body = _encode_binary_value_tree(
            body,
            tuple(),
            packed,
            binary_encoding.encode_map,
            binary_encoding.pack_site_lookup,
        )
        return msgpack.dumps([headers, encoded_body])

    def from_json(self, bytes_: bytes) -> object:
        return json.loads(bytes_)

    def from_msgpack(self, bytes_: bytes) -> object:
        return msgpack.loads(bytes_, strict_map_key=False)

    def split_msgpack_message(self, bytes_: bytes) -> tuple[object, object]:
        message = msgpack.loads(bytes_, raw=False, strict_map_key=False)
        if type(message) is not list:
            raise ValueError("Telepact msgpack payload must be a two-item array")
        message_list = cast(list[object], message)
        if len(message_list) != 2:
            raise ValueError("Telepact msgpack payload must be a two-item array")
        return message_list[0], message_list[1]

    def from_binary_msgpack_body(self, body_value: bytes | object, binary_encoding: 'BinaryEncoding',
                                 packed: bool) -> dict[str, object]:
        if type(body_value) is bytes:
            decoded_body = msgpack.loads(body_value, raw=False, strict_map_key=False)
        else:
            decoded_body = body_value

        if not packed:
            return cast(dict[str, object], _decode_binary_keys_only(decoded_body, binary_encoding.decode_table))

        value = _decode_binary_value_tree(
            decoded_body,
            tuple(),
            packed,
            binary_encoding.decode_table,
            binary_encoding.pack_site_lookup,
        )
        return cast(dict[str, object], value)
