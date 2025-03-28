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
    print(f"server_base64_decode called with body: {body}, bytes_paths: {bytes_paths}")
    travel_base64_decode(body, bytes_paths)

def travel_base64_decode(value: object, bytes_paths: object) -> object:
    print(f"travel_base64_decode called with value: {value}, bytes_paths: {bytes_paths}")
    if isinstance(bytes_paths, dict):
        for key, val in bytes_paths.items():
            print(f"Processing key: {key}, val: {val}")
            if val is True:
                if key == "*" and isinstance(value, list):
                    print(f"Decoding list at key: {key}")
                    for i, v in enumerate(value):
                        print(f"Decoding list item at index {i}: {v}")
                        nv = travel_base64_decode(v, val)
                        value[i] = nv
                elif key == "*" and isinstance(value, dict):
                    print(f"Decoding dict at key: {key}")
                    for k, v in value.items():
                        print(f"Decoding dict item with key {k}: {v}")
                        nv = travel_base64_decode(v, val)
                        value[k] = nv
                elif isinstance(value, dict):
                    print(f"Decoding dict value for key {key}")
                    nv = travel_base64_decode(value[key], val)
                    value[key] = nv
                else:
                    raise ValueError(f"Invalid bytes path: {key} for value: {value}")
            else:
                if key == "*" and isinstance(value, list):
                    print(f"Traversing list at key: {key}")
                    for i, v in enumerate(value):
                        print(f"Traversing list item at index {i}: {v}")
                        travel_base64_decode(v, val)
                elif key == "*" and isinstance(value, dict):
                    print(f"Traversing dict at key: {key}")
                    for k, v in value.items():
                        print(f"Traversing dict item with key {k}: {v}")
                        travel_base64_decode(v, val)
                elif isinstance(value, dict):
                    print(f"Traversing dict value for key {key}")
                    travel_base64_decode(value[key], val)
                else:
                    raise ValueError(f"Invalid bytes path: {key} for value: {value}")
        return None
    elif bytes_paths is True and (type(value) is str or value is None):
        print(f"Base64 decoding value: {value}")
        if value is None:
            return None
        decoded_value = base64.b64decode(value.encode("utf-8"))
        print(f"Decoded value: {decoded_value}")
        return decoded_value
    else:
        raise ValueError(f"Invalid bytes path: {bytes_paths} for value: {value} of type {type(value)}")