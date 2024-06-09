from typing import object


class Serialization:
    """
    A serialization implementation that converts between pseudo-JSON Objects and
    byte array JSON payloads.

    Pseudo-JSON objects are defined as data structures that represent JSON
    objects as dicts and JSON arrays as lists.
    """

    def to_json(self, message: object) -> bytes:
        pass

    def to_msg_pack(self, message: object) -> bytes:
        pass

    def from_json(self, bytes_: bytes) -> object:
        pass

    def from_msg_pack(self, bytes_: bytes) -> object:
        pass
