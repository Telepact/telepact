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

    def to_json(self, uapi_message: Any) -> bytes:
        return json.dumps(uapi_message).encode()

    def to_msgpack(self, uapi_message: Any) -> bytes:
        return msgpack.dumps(uapi_message)

    def from_json(self, bytes_: bytes) -> Any:
        return json.loads(bytes_)

    def from_msgpack(self, bytes_: bytes) -> Any:
        return msgpack.loads(bytes_, strict_map_key=False)
