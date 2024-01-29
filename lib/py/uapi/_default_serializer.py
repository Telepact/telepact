from typing import Any, Dict, List, Union
import msgpack
import json
import uapi.types as types


class _DefaultSerializer(types.SerializationImpl):
    class MessagePackMapDeserializer(msgpack.Unpacker):
        @staticmethod
        def deserialize_key(s: str) -> Union[int, str]:
            if isinstance(s, str):
                return s
            return int(s)

    class MessagePackUntypedObjectDeserializer(msgpack.Unpacker):
        pass

    def __init__(self):
        self.json_mapper = json
        self.binary_mapper = msgpack

    def to_json(self, uapi_message: Any) -> bytes:
        return self.json_mapper.dumps(uapi_message)

    def to_msgpack(self, uapi_message: Any) -> bytes:
        return self.binary_mapper.dumps(uapi_message)

    def from_json(self, bytes_: bytes) -> Any:
        return self.json_mapper.loads(bytes_)

    def from_msgpack(self, bytes_: bytes) -> Any:
        return self.binary_mapper.loads(bytes_)
