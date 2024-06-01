from typing import List
from msgpack import ExtType

from uapi.internal.binary.Unpack import unpack


def unpack_list(lst: List[object]) -> List[object]:
    if not lst:
        return lst

    if not isinstance(lst[0], ExtType) or lst[0].code != -1:
        new_lst = []
        for item in lst:
            new_lst.append(unpack(item))
        return new_lst

    unpacked_lst = []
    headers = lst[1]

    for i in range(2, len(lst)):
        row = lst[i]
        m = unpack_map(row, headers)

        unpacked_lst.append(m)

    return unpacked_lst
