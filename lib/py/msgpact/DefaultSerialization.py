import msgpack
import json

from .Serialization import Serialization


class DefaultSerialization(Serialization):

    def to_json(self, msgpact_message: object) -> bytes:
        return json.dumps(msgpact_message).encode()

    def to_msgpack(self, msgpact_message: object) -> bytes:
        return msgpack.dumps(msgpact_message)

    def from_json(self, bytes_: bytes) -> object:
        return json.loads(bytes_)

    def from_msgpack(self, bytes_: bytes) -> object:
        return msgpack.loads(bytes_, strict_map_key=False)
