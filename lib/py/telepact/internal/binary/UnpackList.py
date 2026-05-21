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

from .BinaryEncoding import BinaryPackHeader
from .PackList import PACKED_BYTE
from .PackMap import UNDEFINED_BYTE


def unpack_row(row: list[object], header: BinaryPackHeader) -> dict[object, object]:
    final_map: dict[object, object] = {}

    for index, value in enumerate(row):
        if index + 1 >= len(header):
            continue

        header_entry = header[index + 1]
        if type(value) is ExtType and value.code == UNDEFINED_BYTE:
            continue

        if type(header_entry) is list:
            if type(value) is list:
                final_map[header_entry[0]] = unpack_row(value, header_entry)
        else:
            final_map[header_entry] = value

    return final_map


def unpack_list(lst: list[object], header: BinaryPackHeader) -> list[object]:
    if not lst:
        return lst

    first_item = lst[0]
    if type(first_item) is not ExtType or first_item.code != PACKED_BYTE:
        return lst

    unpacked_lst: list[object] = []
    for row in lst[1:]:
        unpacked_lst.append(unpack_row(row, header) if type(row) is list else row)

    return unpacked_lst
