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

from msgpack import ExtType
from typing import cast

from ...internal.binary.PackMap import UNDEFINED_BYTE


def unpack_map(row: list[object], header: list[object]) -> dict[int, object]:
    from ...internal.binary.Unpack import unpack

    final_map: dict[int, object] = {}

    for j in range(len(row)):
        key = header[j + 1]
        value = row[j]

        if isinstance(value, ExtType) and value.code == UNDEFINED_BYTE:
            continue

        if isinstance(key, list):
            nested_header = key
            nested_row = cast(list[object], value)
            m = unpack_map(nested_row, nested_header)
            i = nested_header[0]

            final_map[i] = m
        else:
            i = key
            unpacked_value = unpack(value)

            final_map[i] = unpacked_value

    return final_map
