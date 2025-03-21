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

from typing import TYPE_CHECKING

from msgpack import ExtType

if TYPE_CHECKING:
    from ...internal.binary.BinaryPackNode import BinaryPackNode


PACKED_BYTE = 17


def pack_list(lst: list[object]) -> list[object]:
    from ...internal.binary.Pack import pack
    from ...internal.binary.PackMap import pack_map
    from ...internal.binary.CannotPack import CannotPack

    if not lst:
        return lst

    packed_list: list[object] = []
    header: list[object] = []

    packed_list.append(ExtType(PACKED_BYTE, b''))

    header.append(None)

    packed_list.append(header)

    key_index_map: dict[int, BinaryPackNode] = {}
    try:
        for item in lst:
            if isinstance(item, dict):
                row = pack_map(item, header, key_index_map)
                packed_list.append(row)
            else:
                # This list cannot be packed, abort
                raise CannotPack()
        return packed_list
    except CannotPack:
        new_list = [pack(item) for item in lst]
        return new_list
