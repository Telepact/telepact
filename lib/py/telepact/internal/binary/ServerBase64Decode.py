#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from typing import TYPE_CHECKING, cast
import base64


def server_base64_decode(body: dict[str, object], bytes_paths: dict[str, object]) -> None:
    travel_base64_decode(body, bytes_paths)

def travel_base64_decode(value: object, bytes_paths: object) -> object:
    if isinstance(bytes_paths, dict):
        for key, val in bytes_paths.items():
            if val is True:
                if key == "*" and isinstance(value, list):
                    for i, v in enumerate(value):
                        nv = travel_base64_decode(v, val)
                        value[i] = nv
                elif key == "*" and isinstance(value, dict):
                    for k, v in value.items():
                        nv = travel_base64_decode(v, val)
                        value[k] = nv
                elif isinstance(value, dict):
                    nv = travel_base64_decode(value[key], val)
                    value[key] = nv
                else:
                    raise ValueError(f"Invalid bytes path: {key} for value: {value}")
            else:
                if key == "*" and isinstance(value, list):
                    for i, v in enumerate(value):
                        travel_base64_decode(v, val)
                elif key == "*" and isinstance(value, dict):
                    for k, v in value.items():
                        travel_base64_decode(v, val)
                elif isinstance(value, dict):
                    travel_base64_decode(value[key], val)
                else:
                    raise ValueError(f"Invalid bytes path: {key} for value: {value}")
        return None
    elif bytes_paths is True and (type(value) is str or value is None):
        if value is None:
            return None
        decoded_value = base64.b64decode(value.encode("utf-8"))
        return decoded_value
    else:
        raise ValueError(f"Invalid bytes path: {bytes_paths} for value: {value} of type {type(value)}")