#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from typing import TYPE_CHECKING, cast
from msgpack import ExtType

from ...internal.binary.BinaryPackNode import BinaryPackNode
from .CannotPack import CannotPack


UNDEFINED_BYTE = 18
UNDEFINED_EXT = ExtType(UNDEFINED_BYTE, b'')
_PACK = None


def pack_map(m: dict[object, object], header: list[object], key_index_map: dict[int, 'BinaryPackNode']) -> list[object]:
    global _PACK
    if _PACK is None:
        from .Pack import pack as _pack
        _PACK = _pack
    pack = _PACK

    row: list[object] = [UNDEFINED_EXT] * (len(header) - 1)
    header_append = header.append
    row_append = row.append
    key_index_map_get = key_index_map.get

    for key, value in m.items():
        if type(key) is str:
            raise CannotPack()

        key = cast(int, key)
        key_index = key_index_map_get(key)

        if key_index is None:
            final_key_index = BinaryPackNode(len(header) - 1, {})

            if type(value) is dict:
                header_append([key])
            else:
                header_append(key)

            key_index_map[key] = final_key_index
            row_append(UNDEFINED_EXT)
        else:
            final_key_index = key_index

        key_index_value = final_key_index.value
        key_index_nested = final_key_index.nested
        header_value = header[key_index_value + 1]

        packed_value: object

        if type(value) is dict:
            try:
                if type(header_value) is not list:
                    raise TypeError()
                nested_header = cast(list[object], header_value)
            except (IndexError, TypeError):
                raise CannotPack()

            packed_value = pack_map(value, nested_header, key_index_nested)
        else:
            if type(header_value) is list:
                raise CannotPack()

            if type(value) is list:
                packed_value = pack(value)
            else:
                packed_value = value

        row[key_index_value] = packed_value

    return row
