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


def _try_decode_flat_dict_list(value: list[object], decode_map_get: Callable[[object], object | None]) -> list[object] | None:
    if not value:
        return []

    if type(value[0]) is not dict:
        return None

    decoded_list: list[object] = []
    decoded_list_append = decoded_list.append

    for item in value:
        if type(item) is not dict:
            return None

        decoded_item: dict[str, object] = {}
        for key, item_value in item.items():
            item_value_type = type(item_value)
            if item_value_type is dict or item_value_type is list:
                return None

            if type(key) is str:
                decoded_item[key] = item_value
                continue
            else:
                decoded_key = decode_map_get(key)
                if decoded_key is None:
                    raise BinaryEncodingMissing(key)

            decoded_item[str(decoded_key)] = item_value

        decoded_list_append(decoded_item)

    return decoded_list


def _decode_keys_recursive(value: object, decode_map_get: Callable[[object], object | None]) -> object:
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
            decoded[decoded_key] = _decode_keys_recursive(item, decode_map_get)
        return decoded
    if value_type is list:
        decoded_flat_dict_list = _try_decode_flat_dict_list(value, decode_map_get)
        if decoded_flat_dict_list is not None:
            return decoded_flat_dict_list
        return [_decode_keys_recursive(item, decode_map_get) for item in value]
    return value


def decode_keys(given: object, binary_encoder: 'BinaryEncoding') -> object:
    decode_map_get = binary_encoder.decode_map.get

    if isinstance(given, dict):
        return _decode_keys_recursive(given, decode_map_get)
    if isinstance(given, list):
        return _decode_keys_recursive(given, decode_map_get)
    return given
