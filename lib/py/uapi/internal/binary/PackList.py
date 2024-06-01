from typing import List, Dict, Any, Union
from msgpack import ExtType
from uapi.internal.binary.BinaryPackNode import BinaryPackNode
from uapi.internal.binary.Pack import pack
from uapi.internal.binary.PackMap import CannotPack, pack_map

PACKED_BYTE = 17


def pack_list(lst: List[Any]) -> List[Any]:
    if not lst:
        return lst

    packed_list: List[Any] = []
    header: List[Any] = []

    packed_list.append(ExtType(PACKED_BYTE, b''))

    header.append(None)

    packed_list.append(header)

    key_index_map: Dict[int, BinaryPackNode] = {}
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
