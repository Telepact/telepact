from typing import cast
from msgpack import ExtType

from uapi.internal.binary.PackList import PACKED_BYTE
from uapi.internal.binary.Unpack import unpack
from uapi.internal.binary.UnpackMap import unpack_map


def unpack_list(lst: list[object]) -> list[object]:
    if not lst:
        return lst

    if not isinstance(lst[0], ExtType) or lst[0].code != PACKED_BYTE:
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
