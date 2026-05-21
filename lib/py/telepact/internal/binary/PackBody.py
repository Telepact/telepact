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

from .BinaryEncoding import BinaryEncoding
from .PackList import pack_list


def _get_parent_map(root: dict[object, object], path: list[int]) -> dict[object, object] | None:
    current: object = root
    for key in path[:-1]:
        if type(current) is not dict:
            return None
        current = current.get(key)
    return current if type(current) is dict else None


def pack_body(body: dict[object, object], binary_encoding: BinaryEncoding) -> dict[object, object]:
    result = dict(body)

    for packed_site in binary_encoding.packed_sites:
        parent_map = _get_parent_map(result, packed_site.encoded_path)
        if parent_map is None or not packed_site.encoded_path:
            continue
        target_key = packed_site.encoded_path[-1]
        value = parent_map.get(target_key)
        if type(value) is list:
            parent_map[target_key] = pack_list(value, packed_site.header)

    return result
