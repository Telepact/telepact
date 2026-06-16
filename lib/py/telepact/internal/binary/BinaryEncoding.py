#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
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
