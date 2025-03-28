from typing import cast
import base64


def client_base64_encode(message: list[object]) -> None:
    body = cast(dict[str, object], message[1])

    travel_base64_encode(body)


def travel_base64_encode(value: object) -> None:
    if isinstance(value, dict):
        for key, val in value.items():
            if isinstance(val, bytes):
                value[key] = base64.b64encode(val).decode("utf-8")
            else:
                travel_base64_encode(val)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            if isinstance(v, bytes):
                value[i] = base64.b64encode(v).decode("utf-8")
            else:
                travel_base64_encode(v)
