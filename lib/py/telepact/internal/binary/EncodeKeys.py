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


def encode_keys(given: object, binary_encoding: 'BinaryEncoding') -> object:
    encode_map = binary_encoding.encode_map
    encode_map_get = encode_map.get

    def encode_keys_recursive(value: object) -> object:
        if value is None:
            return value

        value_type = type(value)

        if value_type is dict:
            encoded: dict[object, object] = {}
            for key, item in value.items():
                encoded[encode_map_get(key, key)] = encode_keys_recursive(item)
            return encoded
        if value_type is list:
            lst = value
            encoded_list: list[object] = [None] * len(lst)
            for index, item in enumerate(lst):
                encoded_list[index] = encode_keys_recursive(item)
            return encoded_list
        return value

    return encode_keys_recursive(given)
