from typing import TYPE_CHECKING

from msgpack import ExtType

if TYPE_CHECKING:
    from uapi.internal.binary.BinaryPackNode import BinaryPackNode


PACKED_BYTE = 17


def pack_list(lst: list[object]) -> list[object]:
    from uapi.internal.binary.Pack import pack
    from uapi.internal.binary.PackMap import pack_map
    from uapi.internal.binary.CannotPack import CannotPack

    if not lst:
        return lst

    packed_list: list[object] = []
    header: list[object] = []

    packed_list.append(ExtType(PACKED_BYTE, b''))

    header.append(None)

    packed_list.append(header)

    key_index_map: dict[int, BinaryPackNode] = {}
    try:
        for item in lst:
            if isinstance(item, dict):
                row = pack_map(item, header, key_index_map)
                packed_list.append(row)
            else:
                # This list cannot be packed, abort
                raise CannotPack()
        return packed_list
    except CannotPack:
        new_list = [pack(item) for item in lst]
        return new_list
