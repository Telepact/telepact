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

from typing import TYPE_CHECKING
from typing import Callable

from ...internal.binary.BinaryEncodingMissing import BinaryEncodingMissing

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding


def _decode_value(value: object, decode_map_get: Callable[[object], object | None]) -> object:
    value_type = type(value)

    if value_type is dict:
        decoded: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is str:
                decoded_key = key
            else:
                decoded_key = decode_map_get(key)
                if decoded_key is None:
                    raise BinaryEncodingMissing(key)
            decoded[decoded_key] = _decode_value(item, decode_map_get)
        return decoded
    if value_type is list:
        return [_decode_value(item, decode_map_get) for item in value]
    return value


def _decode_dict(items: dict[object, object], binary_encoder: 'BinaryEncoding') -> dict[str, object]:
    return _decode_value(items, binary_encoder.decode_map.get)


def decode_keys(given: object, binary_encoder: 'BinaryEncoding') -> object:
    decode_map_get = binary_encoder.decode_map.get

    if isinstance(given, dict):
        return _decode_dict(given, binary_encoder)
    if isinstance(given, list):
        return _decode_value(given, decode_map_get)
    return given
