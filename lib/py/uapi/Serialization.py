from typing import Any


class Serialization:
    """
    A serialization implementation that converts between pseudo-JSON Objects and
    byte array JSON payloads.

    Pseudo-JSON objects are defined as data structures that represent JSON
    objects as Dicts and JSON arrays as Lists.
    """

    def to_json(self, message: Any) -> bytes:
        pass

    def to_msg_pack(self, message: Any) -> bytes:
        pass

    def from_json(self, bytes_: bytes) -> Any:
        pass

    def from_msg_pack(self, bytes_: bytes) -> Any:
        pass
