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
from threading import Lock

from msgpack import ExtType
from .CannotPack import CannotPack
from .PackMap import pack_map

if TYPE_CHECKING:
    from ...internal.binary.BinaryPackNode import BinaryPackNode


PACKED_BYTE = 17
PACKED_EXT = ExtType(PACKED_BYTE, b'')
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


def _try_pack_flat_map_list(lst: list[object]) -> list[object] | None:
    if not lst:
        return lst

    first_item = lst[0]
    if type(first_item) is not dict:
        return None

    header: list[object] = [None]
    key_index_map: dict[object, int] = {}
    for index, (key, value) in enumerate(first_item.items()):
        if type(key) is str:
            return None
        value_type = type(value)
        if value_type is dict or value_type is list:
            return None
        header.append(key)
        key_index_map[key] = index

    packed_list: list[object] = [PACKED_EXT, header]
    packed_list_append = packed_list.append
    row_width = len(header) - 1

    for item in lst:
        if type(item) is not dict:
            return None

        row: list[object] = [UNDEFINED_EXT] * row_width
        for key, value in item.items():
            if type(key) is str:
                return None
            key_index = key_index_map.get(key)
            if key_index is None:
                return None
            value_type = type(value)
            if value_type is dict or value_type is list:
                return None
            row[key_index] = value

        packed_list_append(row)

    return packed_list


def pack_list(lst: list[object]) -> list[object]:
    packed_flat_map_list = _try_pack_flat_map_list(lst)
    if packed_flat_map_list is not None:
        return packed_flat_map_list

    pack = _get_pack()

    if not lst:
        return lst

    packed_list: list[object] = []
    header: list[object] = []

    packed_list.append(PACKED_EXT)

    header.append(None)

    packed_list.append(header)

    key_index_map: dict[int, BinaryPackNode] = {}
    try:
        for item in lst:
            if type(item) is dict:
                row = pack_map(item, header, key_index_map)
                packed_list.append(row)
            else:
                # This list cannot be packed, abort
                raise CannotPack()
        return packed_list
    except CannotPack:
        new_list = [pack(item) for item in lst]
        return new_list
