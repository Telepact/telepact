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

from typing import cast

from msgpack import ExtType  # type: ignore[import]

from ...internal.binary.Pack import PACKED_BYTE, UNDEFINED_BYTE


def unpack(value: object) -> object:
    if isinstance(value, list):
        return unpack_list(value)
    elif isinstance(value, dict):
        new_dict = {}
        for key, val in value.items():
            new_dict[key] = unpack(val)
        return new_dict
    else:
        return value


def unpack_list(lst: list[object]) -> list[object]:
    if not lst:
        return lst

    if not isinstance(lst[0], ExtType) or lst[0].code != PACKED_BYTE:
        new_lst = []
        for item in lst:
            new_lst.append(unpack(item))
        return new_lst

    unpacked_lst: list[object] = []
    headers = cast(list[object], lst[1])

    for i in range(2, len(lst)):
        row = cast(list[object], lst[i])
        m = unpack_map(row, headers)

        unpacked_lst.append(m)

    return unpacked_lst


def unpack_map(row: list[object], header: list[object]) -> dict[int, object]:
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
