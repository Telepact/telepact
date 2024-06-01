from typing import List, Dict, Any, Union
from msgpack import ExtType

from uapi.internal.binary.PackMap import UNDEFINED_BYTE
from uapi.internal.binary.Unpack import unpack


def unpack_map(row: List[Any], header: List[Any]) -> Dict[int, Union[Dict[int, Any], Any]]:
    final_map: Dict[int, Union[Dict[int, Any], Any]] = {}

    for j in range(len(row)):
        key = header[j + 1]
        value = row[j]

        if isinstance(value, ExtType) and value.type == UNDEFINED_BYTE:
            continue

        if isinstance(key, list):
            nested_header = key
            nested_row = value
            m = unpack_map(nested_row, nested_header)
            i = nested_header[0]

            final_map[i] = m
        else:
            i = key
            # Assuming you have a function called `unpack` defined elsewhere
            unpacked_value = unpack(value)

            final_map[i] = unpacked_value

    return final_map
