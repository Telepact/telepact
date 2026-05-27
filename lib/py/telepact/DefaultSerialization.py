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

from contextvars import ContextVar
import json
from typing import TYPE_CHECKING, cast

import msgpack  # type: ignore[import-untyped]
from .Serialization import Serialization

from .internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError
from .internal.binary.BinaryEncodingMissing import BinaryEncodingMissing

if TYPE_CHECKING:
    from .internal.binary.BinaryEncoding import BinaryEncoding
    from .internal.binary.BinaryEncodingCache import BinaryEncodingCache
    from .internal.binary.ClientBinaryStrategy import ClientBinaryStrategy


PACKED_BYTE = 17
UNDEFINED_BYTE = 18
PACKED_EXT = msgpack.ExtType(PACKED_BYTE, b'')
UNDEFINED_EXT = msgpack.ExtType(UNDEFINED_BYTE, b'')
_MISSING = object()


class BinaryEncoderUnavailableWithHeaders(BinaryEncoderUnavailableError):
    def __init__(self, response_headers: dict[str, object]):
        super().__init__()
        self.response_headers = response_headers

class DefaultSerialization(Serialization):

    def __init__(self) -> None:
        self._binary_role: str | None = None
        self._server_binary_encoding: 'BinaryEncoding | None' = None
        self._client_binary_encoding_cache: 'BinaryEncodingCache | None' = None
        self._client_binary_checksum_strategy: 'ClientBinaryStrategy | None' = None
        self._binary_current_function_name: ContextVar[str | None] = ContextVar(
            "telepact_current_binary_function_name",
            default=None,
        )

    def configure_server_binary(self, binary_encoding: 'BinaryEncoding') -> None:
        self._binary_role = "server"
        self._server_binary_encoding = binary_encoding

    def configure_client_binary(self, binary_encoding_cache: 'BinaryEncodingCache') -> None:
        from .internal.binary.ClientBinaryStrategy import ClientBinaryStrategy

        self._binary_role = "client"
        self._client_binary_encoding_cache = binary_encoding_cache
        self._client_binary_checksum_strategy = ClientBinaryStrategy(binary_encoding_cache)

    def to_json(self, telepact_message: object) -> bytes:
        return json.dumps(telepact_message).encode()

    def to_msgpack(self, telepact_message: object, binary: bool = False) -> bytes:
        if binary:
            return self._to_binary_msgpack(telepact_message)

        return self._pack_stream(telepact_message)

    def from_json(self, bytes_: bytes) -> object:
        return json.loads(bytes_)

    def from_msgpack(self, bytes_: bytes) -> object:
        message = msgpack.loads(bytes_, raw=False, strict_map_key=False)
        if not isinstance(message, list) or len(message) != 2:
            return message

        headers = message[0]
        if isinstance(headers, dict) and "@bin_" in headers:
            binary_encoding, pack_tree = self._select_binary_decode(headers)
            if pack_tree is None:
                from .internal.binary.DecodeBody import decode_body

                return [headers, decode_body(cast(dict[object, object], message[1]), binary_encoding)]
            body = self._decode_loaded_binary_with_pack(message[1], binary_encoding, pack_tree)
            return [headers, body]

        return message

    def cache_binary_headers(self, headers: dict[str, object]) -> bool:
        if self._binary_role != "client":
            return False

        binary_encoding_cache = self._client_binary_encoding_cache
        checksum_strategy = self._client_binary_checksum_strategy
        if binary_encoding_cache is None or checksum_strategy is None:
            return False

        binary_checksums = headers.get("@bin_", [])
        if not isinstance(binary_checksums, list) or not binary_checksums:
            return False

        binary_checksum = binary_checksums[0]
        if not isinstance(binary_checksum, int):
            return False

        encode_map = headers.get("@enc_")
        if isinstance(encode_map, dict):
            pack_encoding = headers.get("@encp_", {})
            binary_encoding_cache.add(
                binary_checksum,
                cast(dict[str, int], encode_map),
                cast(dict[str, object], pack_encoding if isinstance(pack_encoding, dict) else {}),
            )

        checksum_strategy.pin_checksum(binary_checksum)
        return True

    def _to_binary_msgpack(self, telepact_message: object) -> bytes:
        if not isinstance(telepact_message, list) or len(telepact_message) != 2:
            raise BinaryEncoderUnavailableError()

        headers = telepact_message[0]
        body = telepact_message[1]
        if not isinstance(headers, dict) or not isinstance(body, dict):
            raise BinaryEncoderUnavailableError()

        if self._binary_role == "client":
            binary_encoding, pack_tree = self._select_client_binary_encode(headers, body)
        elif self._binary_role == "server":
            binary_encoding, pack_tree = self._select_server_binary_encode(headers, body)
        else:
            raise BinaryEncoderUnavailableError()

        return self._to_binary_msgpack_raw(headers, body, binary_encoding, pack_tree)

    def _to_binary_msgpack_raw(
        self,
        headers: dict[object, object],
        body: dict[object, object],
        binary_encoding: 'BinaryEncoding',
        pack_tree: object,
    ) -> bytes:
        if pack_tree is None:
            from .internal.binary.EncodeBody import encode_body

            return msgpack.dumps([headers, encode_body(cast(dict[str, object], body), binary_encoding)])

        packer = msgpack.Packer(autoreset=False)
        packer.pack_array_header(2)
        self._pack_to(packer, headers)
        self._pack_binary_to(
            packer,
            body,
            binary_encoding.encode_map,
            pack_tree,
        )
        return packer.bytes()

    def _select_client_binary_encode(
        self,
        headers: dict[object, object],
        body: dict[object, object],
    ) -> tuple['BinaryEncoding', object]:
        binary_encoding_cache = self._client_binary_encoding_cache
        checksum_strategy = self._client_binary_checksum_strategy
        if binary_encoding_cache is None or checksum_strategy is None:
            raise BinaryEncoderUnavailableError()

        function_name = next(iter(body))
        if isinstance(function_name, str):
            self._binary_current_function_name.set(function_name)

        force_send_json = headers.pop("_forceSendJson", None)
        checksums = checksum_strategy.get_current_checksums()
        headers["@bin_"] = checksums

        if force_send_json is True or len(checksums) > 1:
            raise BinaryEncoderUnavailableError()

        binary_encoding = binary_encoding_cache.get(checksums[0]) if checksums else None
        if not binary_encoding:
            raise BinaryEncoderUnavailableError()

        pack_tree = binary_encoding.request_pack_tree if headers.get("@pac_") is True else None
        return binary_encoding, pack_tree

    def _select_server_binary_encode(
        self,
        headers: dict[object, object],
        body: dict[object, object],
    ) -> tuple['BinaryEncoding', object]:
        binary_encoding = self._server_binary_encoding
        if binary_encoding is None:
            raise BinaryEncoderUnavailableError()

        client_known_binary_checksums = cast(list[object] | None, headers.pop("@clientKnownBinaryChecksums_", None))
        function_name = headers.pop("@binaryFunction_", None)
        result_tag = next(iter(body))

        if result_tag != "Ok_":
            raise BinaryEncoderUnavailableError()

        if (
            client_known_binary_checksums is None
            or binary_encoding.checksum not in client_known_binary_checksums
        ):
            headers["@enc_"] = binary_encoding.encode_map
            headers["@encp_"] = binary_encoding.pack_encoding

        headers["@bin_"] = [binary_encoding.checksum]
        pack_tree = None
        if headers.get("@pac_") is True and isinstance(function_name, str):
            response_pack_tree = binary_encoding.response_pack_trees.get(function_name)
            if isinstance(response_pack_tree, dict):
                pack_tree = response_pack_tree

        return binary_encoding, pack_tree

    def _build_incompatible_binary_response_headers(
        self,
        request_headers: dict[object, object],
        binary_encoding: 'BinaryEncoding',
    ) -> dict[str, object]:
        response_headers: dict[str, object] = {"@bin_": [binary_encoding.checksum]}

        call_id = request_headers.get("@id_")
        if call_id is not None:
            response_headers["@id_"] = call_id

        response_headers["@enc_"] = binary_encoding.encode_map
        response_headers["@encp_"] = binary_encoding.pack_encoding
        return response_headers

    def _pack_stream(self, value: object) -> bytes:
        packer = msgpack.Packer(autoreset=False)
        self._pack_to(packer, value)
        return packer.bytes()

    def _pack_to(self, packer: msgpack.Packer, value: object) -> None:
        stack: list[object] = [value]

        while stack:
            current = stack.pop()
            current_type = type(current)

            if current_type is dict:
                current_dict = current
                assert isinstance(current_dict, dict)
                packer.pack_map_header(len(current_dict))
                for key, item in reversed(tuple(current_dict.items())):
                    stack.append(item)
                    stack.append(key)
            elif current_type is list:
                current_list = current
                assert isinstance(current_list, list)
                packer.pack_array_header(len(current_list))
                for item in reversed(current_list):
                    stack.append(item)
            else:
                packer.pack(current)

    def _pack_binary_to(
        self,
        packer: msgpack.Packer,
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
                packer.pack_map_header(len(current_dict))
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
                    self._pack_packed_list_to(packer, current_list, current_pack_node, encode_map)
                else:
                    packer.pack_array_header(len(current_list))
                    for item in reversed(current_list):
                        stack.append((item, None))
            else:
                packer.pack(current)

    def _pack_binary_without_pack_to(
        self,
        packer: msgpack.Packer,
        value: object,
        encode_map: dict[str, int],
    ) -> None:
        self._pack_binary_to(packer, value, encode_map, None)

    def _pack_packed_list_to(
        self,
        packer: msgpack.Packer,
        values: list[object],
        header: list[object],
        encode_map: dict[str, int],
    ) -> None:
        if not values:
            packer.pack_array_header(0)
            return

        for value in values:
            if type(value) is not dict or not self._can_pack_struct(value, header):
                packer.pack_array_header(len(values))
                for item in values:
                    self._pack_binary_without_pack_to(packer, item, encode_map)
                return

        packer.pack_array_header(len(values) + 1)
        packer.pack(PACKED_EXT)
        for value in values:
            assert isinstance(value, dict)
            packer.pack(self._build_packed_struct_row(value, header, encode_map))

    def _encode_binary_without_pack(self, value: object, encode_map: dict[str, int]) -> object:
        result: object = None
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

    def _select_binary_decode(self, headers: dict[object, object]) -> tuple['BinaryEncoding', object]:
        binary_checksums = cast(list[object], headers.get("@bin_", []))
        binary_checksum = binary_checksums[0]
        if not isinstance(binary_checksum, int):
            raise BinaryEncoderUnavailableError()

        if self._binary_role == "server":
            binary_encoding = self._server_binary_encoding
            if binary_encoding is None:
                raise BinaryEncoderUnavailableError()
            if binary_checksum != binary_encoding.checksum:
                raise BinaryEncoderUnavailableWithHeaders(
                    self._build_incompatible_binary_response_headers(headers, binary_encoding)
                )
            pack_tree = binary_encoding.request_pack_tree if headers.get("@pac_") is True else None
            return binary_encoding, pack_tree

        if self._binary_role == "client":
            binary_encoding_cache = self._client_binary_encoding_cache
            checksum_strategy = self._client_binary_checksum_strategy
            if binary_encoding_cache is None or checksum_strategy is None:
                raise BinaryEncoderUnavailableError()

            if "@enc_" in headers:
                binary_encoding_cache.add(
                    binary_checksum,
                    cast(dict[str, int], headers["@enc_"]),
                    cast(dict[str, object], headers.get("@encp_", {})),
                )

            checksum_strategy.update_checksum(binary_checksum)
            current_checksums = checksum_strategy.get_current_checksums()
            binary_encoding = binary_encoding_cache.get(current_checksums[0])

            pack_tree = None
            function_name = self._binary_current_function_name.get()
            if headers.get("@pac_") is True and function_name is not None:
                response_pack_tree = binary_encoding.response_pack_trees.get(function_name)
                if isinstance(response_pack_tree, dict):
                    pack_tree = response_pack_tree

            return binary_encoding, pack_tree

        raise BinaryEncoderUnavailableError()

    @staticmethod
    def _next_msgpack_kind(data: bytes, unpacker: msgpack.Unpacker) -> str:
        marker = data[unpacker.tell()]
        if 0x80 <= marker <= 0x8F or marker in (0xDE, 0xDF):
            return "map"
        if 0x90 <= marker <= 0x9F or marker in (0xDC, 0xDD):
            return "array"
        return "scalar"

    @staticmethod
    def _assign_value(parent: object, key: object, value: object) -> object:
        if parent is None:
            return value
        if isinstance(parent, dict):
            parent[key] = value
        else:
            assert isinstance(parent, list)
            assert isinstance(key, int)
            parent[key] = value
        return _MISSING

    def _unpack_stream_value_from(
        self,
        unpacker: msgpack.Unpacker,
        data: bytes,
    ) -> object:
        result = _MISSING
        stack: list[tuple[object, ...]] = []

        def read_value(parent: object, key: object) -> tuple[object, ...] | None:
            nonlocal result
            kind = self._next_msgpack_kind(data, unpacker)

            if kind == "map":
                size = unpacker.read_map_header()
                map_value: dict[object, object] = {}
                assigned = self._assign_value(parent, key, map_value)
                if assigned is not _MISSING:
                    result = assigned
                return ("map", map_value, size) if size else None

            if kind == "array":
                size = unpacker.read_array_header()
                list_value: list[object] = [None] * size
                assigned = self._assign_value(parent, key, list_value)
                if assigned is not _MISSING:
                    result = assigned
                return ("array", list_value, 0, size) if size else None

            value = unpacker.unpack()
            assigned = self._assign_value(parent, key, value)
            if assigned is not _MISSING:
                result = assigned
            return None

        first_frame = read_value(None, None)
        if first_frame is not None:
            stack.append(first_frame)

        while stack:
            frame = stack.pop()
            frame_type = frame[0]

            if frame_type == "array":
                _, target, index, remaining = frame
                assert isinstance(target, list)
                assert isinstance(index, int)
                assert isinstance(remaining, int)
                next_remaining = remaining - 1
                if next_remaining:
                    stack.append(("array", target, index + 1, next_remaining))
                child_frame = read_value(target, index)
                if child_frame is not None:
                    stack.append(child_frame)
            else:
                _, target, remaining = frame
                assert isinstance(target, dict)
                assert isinstance(remaining, int)
                key = unpacker.unpack()
                next_remaining = remaining - 1
                if next_remaining:
                    stack.append(("map", target, next_remaining))
                child_frame = read_value(target, key)
                if child_frame is not None:
                    stack.append(child_frame)

        return None if result is _MISSING else result

    def _unpack_binary_value_from(
        self,
        unpacker: msgpack.Unpacker,
        data: bytes,
        binary_encoding: 'BinaryEncoding',
        pack_tree: object,
    ) -> object:
        decode_table = binary_encoding.decode_table

        def decode_key(key: object) -> str:
            if type(key) is str:
                return key
            try:
                return decode_table[cast(int, key)]
            except (IndexError, TypeError) as exc:
                raise BinaryEncodingMissing(key) from exc

        result = _MISSING
        stack: list[tuple[object, ...]] = []

        def assign(parent: object, key: object, value: object) -> None:
            nonlocal result
            assigned = self._assign_value(parent, key, value)
            if assigned is not _MISSING:
                result = assigned

        def read_packable_array(
            parent: object,
            key: object,
            header: list[object],
        ) -> tuple[object, ...] | None:
            size = unpacker.read_array_header()
            if size == 0:
                assign(parent, key, [])
                return None

            first_kind = self._next_msgpack_kind(data, unpacker)
            if first_kind == "scalar":
                first_item = unpacker.unpack()
                if type(first_item) is msgpack.ExtType and first_item.code == PACKED_BYTE:
                    packed_list: list[object] = []
                    assign(parent, key, packed_list)
                    return ("packed_list", packed_list, size - 1, header) if size > 1 else None

                values: list[object] = [None] * size
                values[0] = first_item
                assign(parent, key, values)
                return ("array", values, 1, size - 1) if size > 1 else None

            values = [None] * size
            assign(parent, key, values)
            return ("array", values, 0, size)

        def read_value(
            parent: object,
            key: object,
            node: object,
        ) -> tuple[object, ...] | None:
            kind = self._next_msgpack_kind(data, unpacker)

            if kind == "map":
                size = unpacker.read_map_header()
                map_value: dict[str, object] = {}
                assign(parent, key, map_value)
                return ("binary_map", map_value, size, node) if size else None

            if kind == "array":
                if isinstance(node, list):
                    return read_packable_array(parent, key, node)

                size = unpacker.read_array_header()
                list_value: list[object] = [None] * size
                assign(parent, key, list_value)
                return ("array", list_value, 0, size) if size else None

            assign(parent, key, unpacker.unpack())
            return None

        def read_packed_row(
            target: list[object],
            header: list[object],
        ) -> tuple[object, ...] | None:
            row = unpacker.unpack()
            if type(row) is list:
                target.append(self._decode_loaded_packed_struct(row, header, binary_encoding))
            else:
                target.append(self._decode_loaded_binary_value(row, binary_encoding))
            return None

        first_frame = read_value(None, None, pack_tree)
        if first_frame is not None:
            stack.append(first_frame)

        while stack:
            frame = stack.pop()
            frame_type = frame[0]

            if frame_type == "array":
                _, target, index, remaining = frame
                assert isinstance(target, list)
                assert isinstance(index, int)
                assert isinstance(remaining, int)
                next_remaining = remaining - 1
                if next_remaining:
                    stack.append(("array", target, index + 1, next_remaining))
                child_frame = read_value(target, index, None)
                if child_frame is not None:
                    stack.append(child_frame)
            elif frame_type == "binary_map":
                _, target, remaining, node = frame
                assert isinstance(target, dict)
                assert isinstance(remaining, int)
                decoded_key = decode_key(unpacker.unpack())
                child_node = node.get(decoded_key) if isinstance(node, dict) else None
                next_remaining = remaining - 1
                if next_remaining:
                    stack.append(("binary_map", target, next_remaining, node))
                child_frame = read_value(target, decoded_key, child_node)
                if child_frame is not None:
                    stack.append(child_frame)
            elif frame_type == "packed_list":
                _, target, remaining, header = frame
                assert isinstance(target, list)
                assert isinstance(remaining, int)
                assert isinstance(header, list)
                next_remaining = remaining - 1
                if next_remaining:
                    stack.append(("packed_list", target, next_remaining, header))
                child_frame = read_packed_row(target, header)
                if child_frame is not None:
                    stack.append(child_frame)
            else:
                raise AssertionError(f"Unknown msgpack decode frame: {frame_type!r}")

        return None if result is _MISSING else result

    @staticmethod
    def _decode_loaded_binary_value(value: object, binary_encoding: 'BinaryEncoding') -> object:
        decode_table = binary_encoding.decode_table

        def decode_key(key: object) -> str:
            if type(key) is str:
                return key
            try:
                return decode_table[cast(int, key)]
            except (IndexError, TypeError) as exc:
                raise BinaryEncodingMissing(key) from exc

        result = _MISSING
        stack: list[tuple[object, object, object]] = [(value, None, None)]

        while stack:
            current, parent, parent_key = stack.pop()
            current_type = type(current)

            if current_type is dict:
                decoded: dict[str, object] = {}
                assigned = DefaultSerialization._assign_value(parent, parent_key, decoded)
                if assigned is not _MISSING:
                    result = assigned

                current_dict = current
                assert isinstance(current_dict, dict)
                for key, item in reversed(tuple(current_dict.items())):
                    stack.append((item, decoded, decode_key(key)))
            elif current_type is list:
                current_list = current
                assert isinstance(current_list, list)
                decoded_list: list[object] = [None] * len(current_list)
                assigned = DefaultSerialization._assign_value(parent, parent_key, decoded_list)
                if assigned is not _MISSING:
                    result = assigned

                for index in range(len(current_list) - 1, -1, -1):
                    stack.append((current_list[index], decoded_list, index))
            else:
                assigned = DefaultSerialization._assign_value(parent, parent_key, current)
                if assigned is not _MISSING:
                    result = assigned

        return None if result is _MISSING else result

    @staticmethod
    def _decode_loaded_binary_with_pack(
        value: object,
        binary_encoding: 'BinaryEncoding',
        pack_node: object,
    ) -> object:
        decode_table = binary_encoding.decode_table

        def decode_key(key: object) -> str:
            if type(key) is str:
                return key
            try:
                return decode_table[cast(int, key)]
            except (IndexError, TypeError) as exc:
                raise BinaryEncodingMissing(key) from exc

        result = _MISSING
        stack: list[tuple[object, object, object, object]] = [(value, None, None, pack_node)]

        while stack:
            current, parent, parent_key, current_pack_node = stack.pop()
            current_type = type(current)

            if current_type is dict:
                decoded: dict[str, object] = {}
                assigned = DefaultSerialization._assign_value(parent, parent_key, decoded)
                if assigned is not _MISSING:
                    result = assigned

                current_dict = current
                assert isinstance(current_dict, dict)
                for key, item in reversed(tuple(current_dict.items())):
                    decoded_key = decode_key(key)
                    child_pack_node = (
                        current_pack_node.get(decoded_key)
                        if isinstance(current_pack_node, dict)
                        else None
                    )
                    stack.append((item, decoded, decoded_key, child_pack_node))
            elif current_type is list:
                current_list = current
                assert isinstance(current_list, list)
                if (
                    isinstance(current_pack_node, list)
                    and current_list
                    and type(current_list[0]) is msgpack.ExtType
                    and current_list[0].code == PACKED_BYTE
                ):
                    packed_list = [
                        DefaultSerialization._decode_loaded_packed_struct(
                            cast(list[object], row),
                            current_pack_node,
                            binary_encoding,
                        )
                        if type(row) is list
                        else DefaultSerialization._decode_loaded_binary_value(row, binary_encoding)
                        for row in current_list[1:]
                    ]
                    assigned = DefaultSerialization._assign_value(parent, parent_key, packed_list)
                    if assigned is not _MISSING:
                        result = assigned
                    continue

                decoded_list: list[object] = [None] * len(current_list)
                assigned = DefaultSerialization._assign_value(parent, parent_key, decoded_list)
                if assigned is not _MISSING:
                    result = assigned

                for index in range(len(current_list) - 1, -1, -1):
                    stack.append((current_list[index], decoded_list, index, None))
            else:
                assigned = DefaultSerialization._assign_value(parent, parent_key, current)
                if assigned is not _MISSING:
                    result = assigned

        return None if result is _MISSING else result

    @staticmethod
    def _decode_loaded_packed_struct(
        row: list[object],
        header: list[object],
        binary_encoding: 'BinaryEncoding',
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
                    elif type(value) is dict:
                        target[key] = DefaultSerialization._decode_loaded_binary_value(
                            value,
                            binary_encoding,
                        )
                    else:
                        target[key] = value
                else:
                    target[cast(str, header_entry)] = (
                        DefaultSerialization._decode_loaded_binary_value(value, binary_encoding)
                        if type(value) is dict or type(value) is list
                        else value
                    )

        return decoded
