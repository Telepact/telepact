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
