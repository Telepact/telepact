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

from .PackList import PACKED_BYTE
from .PackMap import UNDEFINED_BYTE


def _unpack_row(row: list[object], header: list[object]) -> dict[object, object]:
    unpacked_row: dict[object, object] = {}
    for index, header_entry in enumerate(header[1:]):
        if index >= len(row):
            break
        value = row[index]
        if type(value) is ExtType and value.code == UNDEFINED_BYTE:
            continue
        if isinstance(header_entry, list):
            nested_key = header_entry[0]
            if value is None:
                unpacked_row[nested_key] = None
                continue
            if type(value) is not list:
                continue
            unpacked_row[nested_key] = _unpack_row(value, header_entry)
            continue
        unpacked_row[header_entry] = value
    return unpacked_row


def _unpack_site(value: object, header: list[object]) -> object:
    if type(value) is not list or len(value) < 2:
        return value
    packed_type = value[0]
    if type(packed_type) is not ExtType or packed_type.code != PACKED_BYTE:
        return value
    if value[1] != header:
        return value
    return [_unpack_row(row, header) for row in value[2:] if type(row) is list]


def unpack_body(body: dict[object, object], binary_encoding: object) -> dict[object, object]:
    unpacked_body = dict(body)
    for path, header in binary_encoding.encoded_pack_sites:
        current: object = unpacked_body
        for key in path[:-1]:
            if type(current) is not dict or key not in current:
                current = None
                break
            current = current[key]
        if type(current) is not dict:
            continue
        final_key = path[-1]
        if final_key not in current:
            continue
        current[final_key] = _unpack_site(current[final_key], header)
    return unpacked_body
