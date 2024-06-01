from typing import Any, Dict


def unpack_body(body: Dict[Any, Any]) -> Dict[Any, Any]:
    from uapi.internal.binary.Unpack import unpack

    result = {}

    for key, value in body.items():
        unpacked_value = unpack(value)
        result[key] = unpacked_value

    return result
