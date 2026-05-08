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
