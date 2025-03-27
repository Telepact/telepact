from abc import ABCMeta, abstractmethod
from typing import Any, TYPE_CHECKING

from ...internal.binary.BinaryEncodingCache import BinaryEncodingCache

if TYPE_CHECKING:
    from .BinaryEncoding import BinaryEncoding

class DefaultBinaryEncodingCache(BinaryEncodingCache):

    def __init__(self) -> None:
        self.recent_binary_encoders: dict[int, 'BinaryEncoding'] = {}

    def add(self, checksum: int, binary_encoding_map: dict[str, int]) -> None:
        """
        Set a binary encoding in the cache.

        Args:
            binary_encoding: The binary encoding.
            checksum: The checksum of the binary encoding.
        """
        from .BinaryEncoding import BinaryEncoding        
        binary_encoding = BinaryEncoding(binary_encoding_map, checksum)
        self.recent_binary_encoders[checksum] = binary_encoding

    def get(self, checksum: int) -> 'BinaryEncoding':
        """
        Get a binary encoding from the cache.

        Args:
            checksum: The checksum of the binary encoding.

        Returns:
            The binary encoding.
        """
        return self.recent_binary_encoders[checksum]

    def remove(self, checksum: int) -> None:
        """
        Delete a binary encoding from the cache.

        Args:
            checksum: The checksum of the binary encoding.
        """
        self.recent_binary_encoders.pop(checksum, None)