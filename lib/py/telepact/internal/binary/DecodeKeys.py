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


def decode_keys(given: object, binary_encoder: 'BinaryEncoding') -> object:
    from ...internal.binary.BinaryEncodingMissing import BinaryEncodingMissing

    if isinstance(given, dict):
        new_dict: dict[str, object] = {}

        for key, value in given.items():
            if isinstance(key, str):
                new_key = key
            else:
                possible_new_key = binary_encoder.decode_map.get(key)

                if possible_new_key is None:
                    raise BinaryEncodingMissing(key)

                new_key = possible_new_key

            encoded_value = decode_keys(value, binary_encoder)
            new_dict[new_key] = encoded_value

        return new_dict
    elif isinstance(given, list):
        return [decode_keys(item, binary_encoder) for item in given]
    else:
        return given
