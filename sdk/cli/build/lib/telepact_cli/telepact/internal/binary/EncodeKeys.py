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
    if given is None:
        return given
    elif isinstance(given, dict):
        new_dict: dict[object, object] = {}

        for key, value in given.items():
            final_key = binary_encoding.encode_map.get(key, key)
            encoded_value = encode_keys(value, binary_encoding)

            new_dict[final_key] = encoded_value

        return new_dict
    elif isinstance(given, list):
        return [encode_keys(item, binary_encoding) for item in given]
    else:
        return given
