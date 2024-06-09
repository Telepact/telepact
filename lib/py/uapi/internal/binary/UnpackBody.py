from typing import object, dict


def unpack_body(body: dict[object, object]) -> dict[object, object]:
    from uapi.internal.binary.Unpack import unpack

    result = {}

    for key, value in body.items():
        unpacked_value = unpack(value)
        result[key] = unpacked_value

    return result
