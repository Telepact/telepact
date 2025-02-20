from typing import TYPE_CHECKING, cast
from msgpack import ExtType

from ...internal.binary.BinaryPackNode import BinaryPackNode


UNDEFINED_BYTE = 18


def pack_map(m: dict[object, object], header: list[object], key_index_map: dict[int, 'BinaryPackNode']) -> list[object]:
    from ...internal.binary.CannotPack import CannotPack
    from ...internal.binary.Pack import pack

    row: list[object] = []
    for key, value in m.items():
        if isinstance(key, str):
            raise CannotPack()

        key = cast(int, key)
        key_index = key_index_map.get(key)

        if key_index is None:
            final_key_index = BinaryPackNode(len(header) - 1, {})

            if isinstance(value, dict):
                header.append([key])
            else:
                header.append(key)

            key_index_map[key] = final_key_index
        else:
            final_key_index = key_index

        key_index_value = final_key_index.value
        key_index_nested = final_key_index.nested

        packed_value: object

        if isinstance(value, dict):
            try:
                nested_header = header[key_index_value + 1]
                if not isinstance(nested_header, list):
                    raise TypeError()
            except (IndexError, TypeError):
                raise CannotPack()

            packed_value = pack_map(value, nested_header, key_index_nested)
        else:
            if isinstance(header[key_index_value + 1], list):
                raise CannotPack()

            packed_value = pack(value)

        while len(row) < key_index_value:
            row.append(ExtType(UNDEFINED_BYTE, b''))

        if len(row) == key_index_value:
            row.append(packed_value)
        else:
            row[key_index_value] = packed_value

    return row
