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
from .internal.binary.BinaryEncodingMissing import BinaryEncodingMissing


PACKED_BYTE = 17
UNDEFINED_BYTE = 18
PACKED_EXT = msgpack.ExtType(PACKED_BYTE, b'')
UNDEFINED_EXT = msgpack.ExtType(UNDEFINED_BYTE, b'')
_MISSING = object()


class DefaultSerialization(Serialization):

    def to_json(self, telepact_message: object) -> bytes:
        return json.dumps(telepact_message).encode()

    def to_msgpack(self, telepact_message: object) -> bytes:
        from .internal.binary.BinaryEncodedMessage import BinaryEncodedMessage

        if isinstance(telepact_message, BinaryEncodedMessage):
            return self._to_binary_msgpack(telepact_message)

        return self._pack_stream(telepact_message)

    def from_json(self, bytes_: bytes) -> object:
        return json.loads(bytes_)

    def from_msgpack(self, bytes_: bytes) -> object:
        unpacker = msgpack.Unpacker(raw=False, strict_map_key=False)
        unpacker.feed(bytes_)
        return unpacker.unpack()

    def _to_binary_msgpack(self, telepact_message: object) -> bytes:
        from .internal.binary.BinaryEncodedMessage import BinaryEncodedMessage

        binary_message = telepact_message
        assert isinstance(binary_message, BinaryEncodedMessage)

        packer = msgpack.Packer()
        out = bytearray()
        out.extend(packer.pack_array_header(2))
        self._pack_to(packer, out, binary_message.headers)
        self._pack_binary_to(
            packer,
            out,
            binary_message.body,
            binary_message.binary_encoding.encode_map,
            binary_message.pack_tree,
        )
        return bytes(out)

    def _pack_stream(self, value: object) -> bytes:
        packer = msgpack.Packer()
        out = bytearray()
        self._pack_to(packer, out, value)
        return bytes(out)

    def _pack_to(self, packer: msgpack.Packer, out: bytearray, value: object) -> None:
        stack: list[object] = [value]

        while stack:
            current = stack.pop()
            current_type = type(current)

            if current_type is dict:
                current_dict = current
                assert isinstance(current_dict, dict)
                out.extend(packer.pack_map_header(len(current_dict)))
                for key, item in reversed(tuple(current_dict.items())):
                    stack.append(item)
                    stack.append(key)
            elif current_type is list:
                current_list = current
                assert isinstance(current_list, list)
                out.extend(packer.pack_array_header(len(current_list)))
                for item in reversed(current_list):
                    stack.append(item)
            else:
                out.extend(packer.pack(current))

    def _pack_binary_to(
        self,
        packer: msgpack.Packer,
        out: bytearray,
        value: object,
        encode_map: dict[str, int],
        pack_node: object,
    ) -> None:
        stack: list[tuple[object, object]] = [(value, pack_node)]

        while stack:
            current, current_pack_node = stack.pop()
            current_type = type(current)

            if current_type is dict:
                current_dict = current
                assert isinstance(current_dict, dict)
                out.extend(packer.pack_map_header(len(current_dict)))
                for key, item in reversed(tuple(current_dict.items())):
                    encoded_key = encode_map.get(key, key) if type(key) is str else key
                    child_pack_node = (
                        current_pack_node.get(key)
                        if isinstance(current_pack_node, dict)
                        else None
                    )
                    stack.append((item, child_pack_node))
                    stack.append((encoded_key, None))
            elif current_type is list:
                current_list = current
                assert isinstance(current_list, list)
                if isinstance(current_pack_node, list):
                    self._pack_packed_list_to(packer, out, current_list, current_pack_node, encode_map)
                else:
                    out.extend(packer.pack_array_header(len(current_list)))
                    for item in reversed(current_list):
                        stack.append((item, None))
            else:
                out.extend(packer.pack(current))

    def _pack_binary_without_pack_to(
        self,
        packer: msgpack.Packer,
        out: bytearray,
        value: object,
        encode_map: dict[str, int],
    ) -> None:
        self._pack_binary_to(packer, out, value, encode_map, None)

    def _pack_packed_list_to(
        self,
        packer: msgpack.Packer,
        out: bytearray,
        values: list[object],
        header: list[object],
        encode_map: dict[str, int],
    ) -> None:
        if not values:
            out.extend(packer.pack_array_header(0))
            return

        for value in values:
            if type(value) is not dict or not self._can_pack_struct(value, header):
                out.extend(packer.pack_array_header(len(values)))
                for item in values:
                    self._pack_binary_without_pack_to(packer, out, item, encode_map)
                return

        out.extend(packer.pack_array_header(len(values) + 1))
        out.extend(packer.pack(PACKED_EXT))
        for value in values:
            assert isinstance(value, dict)
            out.extend(packer.pack(self._build_packed_struct_row(value, header, encode_map)))

    def _encode_binary_without_pack(self, value: object, encode_map: dict[str, int]) -> object:
        result = None
        stack: list[tuple[object, object, object]] = [(value, None, None)]

        while stack:
            current, parent, parent_key = stack.pop()
            current_type = type(current)

            if current_type is dict:
                encoded: dict[object, object] = {}
                if parent is None:
                    result = encoded
                elif isinstance(parent, dict):
                    parent[parent_key] = encoded
                else:
                    assert isinstance(parent, list)
                    assert isinstance(parent_key, int)
                    parent[parent_key] = encoded

                current_dict = current
                assert isinstance(current_dict, dict)
                for key, item in reversed(tuple(current_dict.items())):
                    encoded_key = encode_map.get(key, key) if type(key) is str else key
                    stack.append((item, encoded, encoded_key))
            elif current_type is list:
                current_list = current
                assert isinstance(current_list, list)
                encoded_list: list[object] = [None] * len(current_list)
                if parent is None:
                    result = encoded_list
                elif isinstance(parent, dict):
                    parent[parent_key] = encoded_list
                else:
                    assert isinstance(parent, list)
                    assert isinstance(parent_key, int)
                    parent[parent_key] = encoded_list

                for index in range(len(current_list) - 1, -1, -1):
                    stack.append((current_list[index], encoded_list, index))
            else:
                if parent is None:
                    result = current
                elif isinstance(parent, dict):
                    parent[parent_key] = current
                else:
                    assert isinstance(parent, list)
                    assert isinstance(parent_key, int)
                    parent[parent_key] = current

        return result

    def _build_packed_struct_row(
        self,
        value: dict[object, object],
        header: list[object],
        encode_map: dict[str, int],
    ) -> list[object]:
        row: list[object] = [UNDEFINED_EXT] * (len(header) - 1)
        stack: list[tuple[dict[object, object], list[object], list[object]]] = [(value, header, row)]

        while stack:
            current_map, current_header, current_row = stack.pop()
            for index, header_entry in enumerate(current_header[1:]):
                if isinstance(header_entry, list):
                    key = header_entry[0]
                    packed_value = current_map.get(key, _MISSING)
                    if packed_value is _MISSING:
                        current_row[index] = UNDEFINED_EXT
                    elif packed_value is None:
                        current_row[index] = None
                    elif type(packed_value) is dict:
                        nested_map = packed_value
                        assert isinstance(nested_map, dict)
                        nested_row: list[object] = [UNDEFINED_EXT] * (len(header_entry) - 1)
                        current_row[index] = nested_row
                        stack.append((nested_map, header_entry, nested_row))
                    else:
                        current_row[index] = self._encode_binary_without_pack(packed_value, encode_map)
                else:
                    packed_value = current_map.get(header_entry, _MISSING)
                    if packed_value is _MISSING:
                        current_row[index] = UNDEFINED_EXT
                    elif type(packed_value) is dict or type(packed_value) is list:
                        current_row[index] = self._encode_binary_without_pack(packed_value, encode_map)
                    else:
                        current_row[index] = packed_value

        return row

    def _can_pack_struct(self, value: object, header: list[object]) -> bool:
        if type(value) is not dict:
            return False

        stack: list[tuple[dict[object, object], list[object]]] = [(value, header)]

        while stack:
            current_map, current_header = stack.pop()
            known_keys: set[object] = set()

            for header_entry in current_header[1:]:
                if isinstance(header_entry, list):
                    key = header_entry[0]
                    known_keys.add(key)
                    nested_value = current_map.get(key, _MISSING)
                    if nested_value is _MISSING or nested_value is None:
                        continue
                    if type(nested_value) is not dict:
                        return False
                    stack.append((nested_value, header_entry))
                else:
                    known_keys.add(header_entry)

            for key in current_map:
                if key not in known_keys:
                    return False

        return True

    @staticmethod
    def decode_binary_body(
        encoded_body: object,
        binary_encoding: object,
        pack_tree: dict[str, object] | None,
    ) -> object:
        decode_table = binary_encoding.decode_table

        def decode_key(key: object) -> str:
            if type(key) is str:
                return key
            try:
                return decode_table[key]
            except (IndexError, TypeError) as exc:
                raise BinaryEncodingMissing(key) from exc

        result = None
        stack: list[tuple[object, object, object, object]] = [
            (encoded_body, pack_tree, None, None)
        ]

        while stack:
            value, pack_node, parent, parent_key = stack.pop()
            value_type = type(value)

            if value_type is dict:
                decoded: dict[str, object] = {}
                DefaultSerialization._assign_decoded(parent, parent_key, decoded)
                if parent is None:
                    result = decoded

                value_dict = value
                assert isinstance(value_dict, dict)
                for key, item in reversed(tuple(value_dict.items())):
                    decoded_key = decode_key(key)
                    child_pack_node = (
                        pack_node.get(decoded_key)
                        if isinstance(pack_node, dict)
                        else None
                    )
                    stack.append((item, child_pack_node, decoded, decoded_key))
            elif value_type is list:
                value_list = value
                assert isinstance(value_list, list)
                if isinstance(pack_node, list) and DefaultSerialization._is_packed_list(value_list):
                    decoded_value = DefaultSerialization._decode_packed_list(
                        value_list,
                        pack_node,
                        binary_encoding,
                    )
                    DefaultSerialization._assign_decoded(parent, parent_key, decoded_value)
                    if parent is None:
                        result = decoded_value
                else:
                    decoded_list: list[object] = [None] * len(value_list)
                    DefaultSerialization._assign_decoded(parent, parent_key, decoded_list)
                    if parent is None:
                        result = decoded_list
                    for index in range(len(value_list) - 1, -1, -1):
                        stack.append((value_list[index], None, decoded_list, index))
            else:
                DefaultSerialization._assign_decoded(parent, parent_key, value)
                if parent is None:
                    result = value

        return result

    @staticmethod
    def _assign_decoded(parent: object, key: object, value: object) -> None:
        if parent is None:
            return
        if isinstance(parent, dict):
            parent[key] = value
        else:
            assert isinstance(parent, list)
            assert isinstance(key, int)
            parent[key] = value

    @staticmethod
    def _is_packed_list(value: list[object]) -> bool:
        if not value:
            return False
        first_item = value[0]
        return type(first_item) is msgpack.ExtType and first_item.code == PACKED_BYTE

    @staticmethod
    def _decode_plain_binary_value(value: object, binary_encoding: object) -> object:
        return DefaultSerialization.decode_binary_body(value, binary_encoding, None)

    @staticmethod
    def _decode_packed_list(
        value: list[object],
        header: list[object],
        binary_encoding: object,
    ) -> list[object]:
        decoded: list[object] = []
        for index in range(1, len(value)):
            row = value[index]
            if type(row) is list:
                decoded.append(DefaultSerialization._decode_packed_struct(row, header, binary_encoding))
            else:
                decoded.append(DefaultSerialization._decode_plain_binary_value(row, binary_encoding))
        return decoded

    @staticmethod
    def _decode_packed_struct(
        row: list[object],
        header: list[object],
        binary_encoding: object,
    ) -> dict[str, object]:
        decoded: dict[str, object] = {}
        stack: list[tuple[dict[str, object], list[object], list[object]]] = [
            (decoded, row, header)
        ]

        while stack:
            target, current_row, current_header = stack.pop()
            entry_count = min(len(current_row), len(current_header) - 1)

            for index in range(entry_count):
                value = current_row[index]
                if type(value) is msgpack.ExtType and value.code == UNDEFINED_BYTE:
                    continue

                header_entry = current_header[index + 1]
                if isinstance(header_entry, list):
                    key = header_entry[0]
                    if value is None:
                        target[key] = None
                    elif type(value) is list:
                        nested: dict[str, object] = {}
                        target[key] = nested
                        stack.append((nested, value, header_entry))
                    else:
                        target[key] = (
                            DefaultSerialization._decode_plain_binary_value(value, binary_encoding)
                            if type(value) is dict or type(value) is list
                            else value
                        )
                else:
                    target[header_entry] = (
                        DefaultSerialization._decode_plain_binary_value(value, binary_encoding)
                        if type(value) is dict or type(value) is list
                        else value
                    )

        return decoded
