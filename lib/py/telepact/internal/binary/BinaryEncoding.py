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


def _normalize_pack_site_node(node: object) -> object:
    if type(node) is list:
        return cast(list[object], node)

    if type(node) is not dict:
        raise ValueError("pack site metadata must be a nested dict tree terminating in header lists")

    normalized: dict[str, object] = {}
    for raw_key, child in cast(dict[object, object], node).items():
        if type(raw_key) is not str:
            raise ValueError("pack site tree keys must be strings")
        normalized[raw_key] = _normalize_pack_site_node(child)

    return normalized


class BinaryEncoding:
    def __init__(self, binary_encoding_map: dict[str, int], checksum: int,
                 pack_site_tree: dict[str, object] | None = None) -> None:
        self.encode_map: dict[str, int] = binary_encoding_map
        decode_table: list[str | None] = [None] * len(binary_encoding_map)
        for key, value in binary_encoding_map.items():
            if value < 0 or value >= len(decode_table):
                raise ValueError("binary encoding ids must be dense sequential integers")
            if decode_table[value] is not None:
                raise ValueError("binary encoding ids must be unique")
            decode_table[value] = key
        if any(key is None for key in decode_table):
            raise ValueError("binary encoding ids must be dense sequential integers")
        self.decode_table: list[str] = [key for key in decode_table if key is not None]
        self.checksum: int = checksum
        self.pack_site_tree: dict[str, object] = cast(
            dict[str, object], _normalize_pack_site_node(pack_site_tree or {}))

    def get_response_pack_site_root(self, function_name: object) -> object | None:
        if type(function_name) is not str:
            return None

        function_pack_sites = self.pack_site_tree.get(function_name)
        if type(function_pack_sites) is not dict:
            return None

        return cast(dict[str, object], function_pack_sites).get("->")
