from typing import Any, Dict
from uapi.internal.binary.Pack import pack


def pack_body(body: Dict[Any, Any]) -> Dict[Any, Any]:
    result = {}

    for key, value in body.items():
        packed_value = pack(value)
        result[key] = packed_value

    return result
