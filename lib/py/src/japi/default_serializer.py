import json
from serializer import Serializer
from serialization_error import SerializationError
from deserialization_error import DeserializationError
import msgpack
from typing import List


class DefaultSerializer(Serializer):
    def __init__(self):
        self.json_mapper = json.JSONEncoder()
        self.binary_mapper = msgpack.Packer()

    def serialize_to_json(self, japi_message: List[object]) -> bytes:
        try:
            return self.json_mapper.encode(japi_message).encode()
        except Exception as e:
            raise SerializationError(e)

    def serialize_to_msgpack(self, japi_message: List[object]) -> bytes:
        try:
            return self.binary_mapper.pack(japi_message)
        except Exception as e:
            raise SerializationError(e)

    def deserialize_from_json(self, bytes: bytes) -> List[object]:
        try:
            return json.loads(bytes)
        except Exception as e:
            raise DeserializationError(e)

    def deserialize_from_msgpack(self, bytes: bytes) -> List[object]:
        try:
            return msgpack.unpackb(bytes, raw=False)
        except Exception as e:
            raise DeserializationError(e)
