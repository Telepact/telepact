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

    def encode_keys_recursive(value: object) -> object:
        if value is None:
            return value

        value_type = type(value)

        if value_type is list:
            uniform_result = try_encode_uniform_dict_list(value)
            if uniform_result is not None:
                return uniform_result
            return [encode_keys_recursive(item) for item in value]
        if value_type is dict:
            return {
                encode_map.get(key, key): encode_keys_recursive(item)
                for key, item in value.items()
            }
        return value

    def try_encode_uniform_dict_list(value: list[object]) -> list[dict[object, object]] | None:
        if len(value) < 16:
            return None

        first = value[0]
        if type(first) is not dict or not first:
            return None

        keys = list(first.keys())
        encoded_keys: list[object] = []
        for key in keys:
            encoded = encode_map.get(key)
            if encoded is None:
                return None
            encoded_keys.append(encoded)

        result: list[dict[object, object]] = []
        for item in value:
            if type(item) is not dict:
                return None
            result.append({
                encoded_keys[index]: encode_keys_recursive(item.get(keys[index]))
                for index in range(len(keys))
            })
        return result

    return encode_keys_recursive(given)
