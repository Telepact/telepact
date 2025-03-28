from typing import Any, TYPE_CHECKING

from ...internal.binary.BinaryEncodingCache import BinaryEncodingCache

if TYPE_CHECKING:
    from .BinaryEncoding import BinaryEncoding

class DefaultBinaryEncodingCache(BinaryEncodingCache):

    def __init__(self) -> None:
        self.recent_binary_encoders: dict[int, 'BinaryEncoding'] = {}

    def add(self, checksum: int, binary_encoding_map: dict[str, int]) -> None:
        from .BinaryEncoding import BinaryEncoding        
        binary_encoding = BinaryEncoding(binary_encoding_map, checksum)
        self.recent_binary_encoders[checksum] = binary_encoding

    def get(self, checksum: int) -> 'BinaryEncoding':
        return self.recent_binary_encoders[checksum]

    def remove(self, checksum: int) -> None:
        self.recent_binary_encoders.pop(checksum, None)