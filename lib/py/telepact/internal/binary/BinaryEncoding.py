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

from dataclasses import dataclass


def _clone_pack_header_value(value: object) -> object:
    if isinstance(value, list):
        return [_clone_pack_header_value(item) for item in value]
    return value


def _encode_pack_header_value(value: object, encode_map: dict[str, int]) -> object:
    if isinstance(value, list):
        return [_encode_pack_header_value(item, encode_map) for item in value]
    if value is None:
        return None
    return encode_map[value]


@dataclass
class BinaryPackSite:
    path: tuple[str, ...]
    header: list[object]
    encoded_path: tuple[int, ...]
    encoded_header: list[object]


class BinaryEncoding:
    def __init__(self, binary_encoding_map: dict[str, int], checksum: int,
                 pack_sites_header: list[list[object]] | None = None) -> None:
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
        self.pack_sites_header: list[list[object]] = []
        self.pack_sites: list[BinaryPackSite] = []
        self.pack_sites_by_path: dict[tuple[str, ...], BinaryPackSite] = {}
        self.pack_sites_by_encoded_path: dict[tuple[int, ...], BinaryPackSite] = {}

        for pack_site in pack_sites_header or []:
            if len(pack_site) != 2:
                raise ValueError("pack sites must be [path, header] pairs")
            raw_path = pack_site[0]
            raw_header = pack_site[1]
            if not isinstance(raw_path, list) or not isinstance(raw_header, list):
                raise ValueError("pack site path and header must be lists")
            path = tuple(raw_path)
            header = _clone_pack_header_value(raw_header)
            encoded_path = tuple(self.encode_map[key] for key in path)
            encoded_header = _encode_pack_header_value(header, self.encode_map)
            site = BinaryPackSite(path, header, encoded_path, encoded_header)
            self.pack_sites_header.append([list(path), _clone_pack_header_value(header)])
            self.pack_sites.append(site)
            self.pack_sites_by_path[path] = site
            self.pack_sites_by_encoded_path[encoded_path] = site
