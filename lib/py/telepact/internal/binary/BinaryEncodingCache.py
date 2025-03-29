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

from abc import ABCMeta, abstractmethod
from typing import Any

from .BinaryEncoding import BinaryEncoding

class BinaryEncodingCache(metaclass=ABCMeta):

    @abstractmethod
    def add(self, checksum: int, binary_encoding_map: dict[str, int]) -> None:
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