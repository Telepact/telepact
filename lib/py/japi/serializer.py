from typing import List


class Serializer:
    def serialize_to_json(self, japi_message: List[object]) -> bytes:
        raise NotImplementedError()

    def serialize_to_msgpack(self, japi_message: List[object]) -> bytes:
        raise NotImplementedError()

    def deserialize_from_json(self, bytes_: bytes) -> List[object]:
        raise NotImplementedError()

    def deserialize_from_msgpack(self, bytes_: bytes) -> List[object]:
        raise NotImplementedError()
