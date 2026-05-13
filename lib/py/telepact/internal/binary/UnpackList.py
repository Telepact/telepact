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
from msgpack import ExtType
from threading import Lock

from ...internal.binary.PackList import PACKED_BYTE
from ...internal.binary.PackMap import UNDEFINED_BYTE
from ...internal.binary.UnpackMap import unpack_map
_UNPACK = None
_UNPACK_LOCK = Lock()


def _get_unpack():
    global _UNPACK
    if _UNPACK is None:
        with _UNPACK_LOCK:
            if _UNPACK is None:
                from ...internal.binary.Unpack import unpack as _unpack
                _UNPACK = _unpack
    return _UNPACK


def _try_unpack_flat_map_list(lst: list[object]) -> list[object] | None:
    if not lst:
        return lst

    first_item = lst[0]
    if type(first_item) is not ExtType or first_item.code != PACKED_BYTE:
        return None

    headers = cast(list[object], lst[1])
    flat_keys: list[int] = []
    for key in headers[1:]:
        if type(key) is list:
            return None
        flat_keys.append(cast(int, key))

    unpacked_lst: list[object] = []
    unpacked_lst_append = unpacked_lst.append
    key_count = len(flat_keys)

    for i in range(2, len(lst)):
        row = lst[i]
        if type(row) is not list:
            return None

        unpacked_item: dict[int, object] = {}
        row = cast(list[object], row)
        row_count = min(len(row), key_count)
        for index in range(row_count):
            value = row[index]
            if type(value) is ExtType:
                if value.code == UNDEFINED_BYTE:
                    continue
                return None
            value_type = type(value)
            if value_type is dict or value_type is list:
                return None
            unpacked_item[flat_keys[index]] = value

        unpacked_lst_append(unpacked_item)

    return unpacked_lst


def unpack_list(lst: list[object]) -> list[object]:
    unpacked_flat_map_list = _try_unpack_flat_map_list(lst)
    if unpacked_flat_map_list is not None:
        return unpacked_flat_map_list

    unpack = _get_unpack()

    if not lst:
        return lst

    first_item = lst[0]
    if type(first_item) is not ExtType or first_item.code != PACKED_BYTE:
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
