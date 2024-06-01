from typing import Dict


class BinaryEncoding:
    def __init__(self, binary_encoding_map: Dict[str, int], checksum: int) -> None:
        self.encode_map: Dict[str, int] = binary_encoding_map
        self.decode_map: Dict[int, str] = {
            v: k for k, v in binary_encoding_map.items()}
        self.checksum: int = checksum
