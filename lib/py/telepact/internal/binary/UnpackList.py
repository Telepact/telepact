#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import cast
from msgpack import ExtType
from threading import Lock

from ...internal.binary.PackList import PACKED_BYTE
from ...internal.binary.UnpackMap import unpack_map
_UNPACK = None
_UNPACK_LOCK = Lock()


def _get_unpack():
    global _UNPACK
    if _UNPACK is None:
        with _UNPACK_LOCK:
            if _UNPACK is None:
                from ...internal.binary.Unpack import unpack as _unpack
                _UNPACK = _unpack
    return _UNPACK


def unpack_list(lst: list[object]) -> list[object]:
    unpack = _get_unpack()

    if not lst:
        return lst

    first_item = lst[0]
    if type(first_item) is not ExtType or first_item.code != PACKED_BYTE:
        new_lst = []
        for item in lst:
            new_lst.append(unpack(item))
        return new_lst

    unpacked_lst: list[object] = []
    headers = cast(list[object], lst[1])

    for i in range(2, len(lst)):
        row = cast(list[object], lst[i])
        m = unpack_map(row, headers)

        unpacked_lst.append(m)

    return unpacked_lst
