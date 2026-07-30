#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING, cast
import base64

def server_base64_encode(message: list[object]) -> None:
    headers = cast(dict[str, object], message[0])
    body = cast(dict[str, object], message[1])

    base64_paths = cast(dict[str, object], headers.get("@base64_", {}))

    travel_base64_encode(body, base64_paths)

def travel_base64_encode(value: object, base64_paths: object) -> object:
    if isinstance(base64_paths, dict):
        for key, val in base64_paths.items():
            if val is True:
                if key == "*" and isinstance(value, list):
                    for i, v in enumerate(value):
                        nv = travel_base64_encode(v, val)
                        value[i] = nv
                elif key == "*" and isinstance(value, dict):
                    for k, v in value.items():
                        nv = travel_base64_encode(v, val)
                        value[k] = nv
                elif isinstance(value, dict):
                    nv = travel_base64_encode(value[key], val)
                    value[key] = nv
                else:
                    raise ValueError(f"Invalid base64 path: {key} for value: {value}")
            else:
                if key == "*" and isinstance(value, list):
                    for i, v in enumerate(value):
                        travel_base64_encode(v, val)
                elif key == "*" and isinstance(value, dict):
                    for k, v in value.items():
                        travel_base64_encode(v, val)
                elif isinstance(value, dict):
                    travel_base64_encode(value[key], val)
                else:
                    raise ValueError(f"Invalid base64 path: {key} for value: {value}")
        return None
    elif base64_paths is True and (isinstance(value, bytes) or value is None):
        if value is None:
            return None
        return base64.b64encode(value).decode("utf-8")
    else:
        raise ValueError(f"Invalid base64 path: {base64_paths} for value: {value}")
