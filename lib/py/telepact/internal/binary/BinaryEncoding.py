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

class BinaryEncoding:
    def __init__(self, binary_encoding_map: dict[str, int], checksum: int) -> None:
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
