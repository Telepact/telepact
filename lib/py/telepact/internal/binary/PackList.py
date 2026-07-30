#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
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


def pack_list(lst: list[object]) -> list[object]:
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
