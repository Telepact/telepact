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
