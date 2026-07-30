#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
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

        if value_type is dict:
            return {
                encode_map.get(key, key): encode_keys_recursive(item)
                for key, item in value.items()
            }
        if value_type is list:
            return [encode_keys_recursive(item) for item in value]
        return value

    return encode_keys_recursive(given)
