#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING, cast
from threading import Lock
from msgpack import ExtType

from ...internal.binary.BinaryPackNode import BinaryPackNode
from .CannotPack import CannotPack


UNDEFINED_BYTE = 18
UNDEFINED_EXT = ExtType(UNDEFINED_BYTE, b'')
_PACK = None
_PACK_LOCK = Lock()


def _get_pack():
    global _PACK
    if _PACK is None:
        with _PACK_LOCK:
            if _PACK is None:
                from .Pack import pack as _pack
                _PACK = _pack
    return _PACK


def pack_map(m: dict[object, object], header: list[object], key_index_map: dict[int, 'BinaryPackNode']) -> list[object]:
    pack = _get_pack()

    row: list[object] = [UNDEFINED_EXT] * (len(header) - 1)
    header_append = header.append
    row_append = row.append
    key_index_map_get = key_index_map.get

    for key, value in m.items():
        if type(key) is str:
            raise CannotPack()

        key = cast(int, key)
        key_index = key_index_map_get(key)

        if key_index is None:
            final_key_index = BinaryPackNode(len(header) - 1, {})

            if type(value) is dict:
                header_append([key])
            else:
                header_append(key)

            key_index_map[key] = final_key_index
            row_append(UNDEFINED_EXT)
        else:
            final_key_index = key_index

        key_index_value = final_key_index.value
        key_index_nested = final_key_index.nested
        header_value = header[key_index_value + 1]

        packed_value: object

        if type(value) is dict:
            try:
                if type(header_value) is not list:
                    raise TypeError()
                nested_header = cast(list[object], header_value)
            except (IndexError, TypeError):
                raise CannotPack()

            packed_value = pack_map(value, nested_header, key_index_nested)
        else:
            if type(header_value) is list:
                raise CannotPack()

            if type(value) is list:
                packed_value = pack(value)
            else:
                packed_value = value

        row[key_index_value] = packed_value

    return row
