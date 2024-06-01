from typing import List

from uapi.internal.binary.Unpack import unpack


def unpack_map(row: List[object], header: List[object]) -> dict:
    final_map = {}

    for j in range(len(row)):
        key = header[j + 1]
        value = row[j]

        if isinstance(value, MessagePackExtensionType) and value.getType() == UNDEFINED_BYTE:
            continue

        if isinstance(key, list):
            nested_header = key
            nested_row = value
            m = unpack_map(nested_row, nested_header)
            i = nested_header[0]

            final_map[i] = m
        else:
            i = key
            unpacked_value = unpack(value)

            final_map[i] = unpacked_value

    return final_map
