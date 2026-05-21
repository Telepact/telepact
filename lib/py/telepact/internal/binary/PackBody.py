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

PACKED_EXT = ExtType(PACKED_BYTE, b'')
UNDEFINED_EXT = ExtType(UNDEFINED_BYTE, b'')
_MISSING = object()


def _pack_row(value: dict[object, object], header: list[object]) -> list[object] | None:
    row: list[object] = [UNDEFINED_EXT] * (len(header) - 1)
    allowed_keys: set[object] = set()
    for index, header_entry in enumerate(header[1:]):
        if isinstance(header_entry, list):
            nested_key = header_entry[0]
            allowed_keys.add(nested_key)
            nested_value = value.get(nested_key, _MISSING)
            if nested_value is _MISSING:
                continue
            if nested_value is None:
                row[index] = None
                continue
            if type(nested_value) is not dict:
                return None
            packed_nested_value = _pack_row(nested_value, header_entry)
            if packed_nested_value is None:
                return None
            row[index] = packed_nested_value
            continue
        allowed_keys.add(header_entry)
        header_value = value.get(header_entry, _MISSING)
        if header_value is _MISSING:
            continue
        row[index] = header_value
    for key in value.keys():
        if key not in allowed_keys:
            return None
    return row


def _pack_site(value: object, header: list[object]) -> object:
    if type(value) is not list or not value:
        return value

    packed_rows: list[object] = [PACKED_EXT, header]
    for item in value:
        if type(item) is not dict:
            return value
        packed_row = _pack_row(item, header)
        if packed_row is None:
            return value
        packed_rows.append(packed_row)

    return packed_rows


def pack_body(body: dict[object, object], binary_encoding: object) -> dict[object, object]:
    packed_body = dict(body)
    for path, header in binary_encoding.encoded_pack_sites:
        current: object = packed_body
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
        current[final_key] = _pack_site(current[final_key], header)
    return packed_body
