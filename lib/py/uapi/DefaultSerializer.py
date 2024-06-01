from typing import Any, Dict, List, Union
import msgpack
import json
import uapi.types as types


class DefaultSerializer(types.SerializationImpl):

    def to_json(self, uapi_message: Any) -> bytes:
        return json.dumps(uapi_message).encode()

    def to_msgpack(self, uapi_message: Any) -> bytes:
        return msgpack.dumps(uapi_message)

    def from_json(self, bytes_: bytes) -> Any:
        return json.loads(bytes_)

    def from_msgpack(self, bytes_: bytes) -> Any:
        return msgpack.loads(bytes_, strict_map_key=False)
