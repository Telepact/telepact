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

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding


def _try_encode_flat_dict_list(value: list[object], encode_map_get) -> list[object] | None:
    if not value:
        return []

    if type(value[0]) is not dict:
        return None

    encoded_list: list[object] = []
    encoded_list_append = encoded_list.append

    for item in value:
        if type(item) is not dict:
            return None

        encoded_item: dict[object, object] = {}
        for key, item_value in item.items():
            item_value_type = type(item_value)
            if item_value_type is dict or item_value_type is list:
                return None
            encoded_key = encode_map_get(key, key)
            encoded_item[encoded_key] = item_value

        encoded_list_append(encoded_item)

    return encoded_list


def encode_keys(given: object, binary_encoding: 'BinaryEncoding') -> object:
    encode_map = binary_encoding.encode_map

    def encode_keys_recursive(value: object) -> object:
        if value is None:
            return value

        value_type = type(value)

        if value_type is dict:
            return {
                encode_map.get(key, key): encode_keys_recursive(item)
                for key, item in value.items()
            }
        if value_type is list:
            encoded_flat_dict_list = _try_encode_flat_dict_list(value, encode_map.get)
            if encoded_flat_dict_list is not None:
                return encoded_flat_dict_list
            return [encode_keys_recursive(item) for item in value]
        return value

    return encode_keys_recursive(given)
