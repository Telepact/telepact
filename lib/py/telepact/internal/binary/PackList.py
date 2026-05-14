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
from .PackMap import UNDEFINED_EXT

PACKED_BYTE = 17
PACKED_EXT = ExtType(PACKED_BYTE, b'')


def pack_row(m: dict[object, object], header: BinaryPackHeader) -> list[object] | None:
    row: list[object] = [UNDEFINED_EXT] * (len(header) - 1)
    expected_keys: set[object] = set()

    for index in range(1, len(header)):
        header_entry = header[index]
        key = header_entry[0] if type(header_entry) is list else header_entry
        expected_keys.add(key)

        if key not in m:
            continue

        value = m[key]
        if type(header_entry) is list:
            if type(value) is not dict:
                return None
            nested_row = pack_row(value, header_entry)
            if nested_row is None:
                return None
            row[index - 1] = nested_row
        else:
            row[index - 1] = value

    if any(key not in expected_keys for key in m.keys()):
        return None

    while row and row[-1] == UNDEFINED_EXT:
        row.pop()

    return row


def pack_list(lst: list[object], header: BinaryPackHeader) -> list[object]:
    if not lst:
        return lst

    packed_list: list[object] = [PACKED_EXT]
    for item in lst:
        if type(item) is not dict:
            return lst
        packed_row = pack_row(item, header)
        if packed_row is None:
            return lst
        packed_list.append(packed_row)

    return packed_list
