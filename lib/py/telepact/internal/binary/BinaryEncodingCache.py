from abc import ABCMeta, abstractmethod
from typing import Any

from .BinaryEncoding import BinaryEncoding

class BinaryEncodingCache(metaclass=ABCMeta):

    @abstractmethod
    def add(self, checksum: int, binary_encoding: dict[str, int]) -> None:
        """
        Set a binary encoding in the cache.

        Args:
            binary_encoding: The binary encoding.
            checksum: The checksum of the binary encoding.
        """
        pass

    @abstractmethod
    def get(self, checksum: int) -> 'BinaryEncoding':
        """
        Get a binary encoding from the cache.

        Args:
            checksum: The checksum of the binary encoding.

        Returns:
            The binary encoding.
        """
        pass

    @abstractmethod
    def remove(self, checksum: int) -> None:
        """
        Delete a binary encoding from the cache.

        Args:
            checksum: The checksum of the binary encoding.
        """
        pass