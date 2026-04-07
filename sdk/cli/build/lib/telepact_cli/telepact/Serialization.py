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


class Serialization(metaclass=ABCMeta):
    """
    A serialization implementation that converts between pseudo-JSON Objects and
    byte array JSON payloads.

    Pseudo-JSON objects are defined as data structures that represent JSON
    objects as dicts and JSON arrays as lists.
    """

    @abstractmethod
    def to_json(self, message: object) -> bytes:
        pass

    @abstractmethod
    def to_msgpack(self, message: object) -> bytes:
        pass

    @abstractmethod
    def from_json(self, bytes_: bytes) -> object:
        pass

    @abstractmethod
    def from_msgpack(self, bytes_: bytes) -> object:
        pass
