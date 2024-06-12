from msgpack import ExtType, cast

from uapi.internal.binary.PackMap import UNDEFINED_BYTE


def unpack_map(row: list[object], header: list[object]) -> dict[int, object]:
    from uapi.internal.binary.Unpack import unpack

    final_map: dict[int, object] = {}

    for j in range(len(row)):
        key = header[j + 1]
        value = row[j]

        if isinstance(value, ExtType) and value.type == UNDEFINED_BYTE:
            continue

        if isinstance(key, list):
            nested_header = key
            nested_row = cast(list[object], value)
            m = unpack_map(nested_row, nested_header)
            i = nested_header[0]

            final_map[i] = m
        else:
            i = key
            # Assuming you have a function called `unpack` defined elsewhere
            unpacked_value = unpack(value)

            final_map[i] = unpacked_value

    return final_map
