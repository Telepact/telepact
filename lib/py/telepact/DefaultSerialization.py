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

def _get_pack_site_child(pack_site_node: object | None, key: object) -> object | None:
    if type(pack_site_node) is dict and type(key) is str:
        return cast(dict[str, object], pack_site_node).get(key)
    return None


def _get_pack_site_root(headers: dict[str, object], body: dict[str, object],
                        binary_encoding: 'BinaryEncoding') -> object | None:
    if not body:
        return None

    target = next(iter(body.keys()))
    if type(target) is str and target.startswith("fn."):
        return binary_encoding.pack_site_tree

    return binary_encoding.get_response_pack_site_root(headers.get("@fn_"))


def _encode_packed_row_tree(row_value: dict[object, object], header: list[object],
                            encode_map: dict[str, int]) -> list[object]:
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
                row_append(_encode_packed_row_tree(cast(dict[object, object], nested_value), nested_header, encode_map))
            else:
                row_append(_encode_binary_value_tree(nested_value, None, encode_map))
        else:
            field_value = row_value.get(entry, MISSING)
            if field_value is MISSING:
                row_append(UNDEFINED_EXT)
            else:
                row_append(_encode_binary_value_tree(field_value, None, encode_map))

    return row


def _encode_binary_value_tree(value: object, pack_site_node: object | None,
                              encode_map: dict[str, int]) -> object:
    if type(value) is dict:
        value_map = cast(dict[object, object], value)
        encoded_map: dict[object, object] = {}
        encoded_map_set = encoded_map.__setitem__

        for key, nested_value in value_map.items():
            if type(key) is str:
                encoded_key: object = encode_map[key]
                next_pack_site = _get_pack_site_child(pack_site_node, key)
            else:
                encoded_key = key
                next_pack_site = None

            encoded_map_set(
                encoded_key,
                _encode_binary_value_tree(nested_value, next_pack_site, encode_map),
            )

        return encoded_map

    if type(value) is list:
        value_list = cast(list[object], value)
        if type(pack_site_node) is list and all(type(item) is dict for item in value_list):
            return [
                PACKED_EXT,
                *[
                    _encode_packed_row_tree(cast(dict[object, object], item), cast(list[object], pack_site_node),
                                            encode_map)
                    for item in value_list
                ],
            ]

        return [_encode_binary_value_tree(item, None, encode_map) for item in value_list]

    return value


def _decode_packed_row_tree(row_value: list[object], header: list[object],
                            decode_table: list[str]) -> dict[str, object]:
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
                _decode_binary_value_tree(value, None, decode_table)
                if type(value) is not list else _decode_packed_row_tree(cast(list[object], value), nested_header, decode_table),
            )
        else:
            row_map_set(cast(str, header_entry), _decode_binary_value_tree(value, None, decode_table))

    return row_map


def _decode_binary_value_tree(value: object, pack_site_node: object | None,
                              decode_table: list[str]) -> object:
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

            next_pack_site = _get_pack_site_child(pack_site_node, key)
            decoded_map_set(
                key,
                _decode_binary_value_tree(nested_value, next_pack_site, decode_table),
            )

        return decoded_map

    if type(value) is list:
        value_list = cast(list[object], value)
        if type(pack_site_node) is list and value_list and type(value_list[0]) is ExtType:
            first_item = cast(ExtType, value_list[0])
            if first_item.code == PACKED_BYTE:
                return [
                    _decode_binary_value_tree(item, None, decode_table)
                    if type(item) is not list
                    else _decode_packed_row_tree(cast(list[object], item), cast(list[object], pack_site_node), decode_table)
                    for item in value_list[1:]
                ]

        return [_decode_binary_value_tree(item, None, decode_table) for item in value_list]

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


class DefaultSerialization(Serialization):

    def to_json(self, telepact_message: object) -> bytes:
        return json.dumps(telepact_message).encode()

    def to_msgpack(self, telepact_message: object) -> bytes:
        return msgpack.dumps(telepact_message)

    def to_binary_msgpack(self, headers: dict[str, object], body: dict[str, object],
                          binary_encoding: 'BinaryEncoding', packed: bool) -> bytes:
        encoded_body = _encode_binary_value_tree(
            body,
            _get_pack_site_root(headers, body, binary_encoding) if packed else None,
            binary_encoding.encode_map,
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
                                 packed: bool, pack_site_root: object | None = None) -> dict[str, object]:
        if type(body_value) is bytes:
            decoded_body = msgpack.loads(body_value, raw=False, strict_map_key=False)
        else:
            decoded_body = body_value

        if not packed:
            return cast(dict[str, object], _decode_binary_keys_only(decoded_body, binary_encoding.decode_table))

        value = _decode_binary_value_tree(
            decoded_body,
            pack_site_root,
            binary_encoding.decode_table,
        )
        return cast(dict[str, object], value)
