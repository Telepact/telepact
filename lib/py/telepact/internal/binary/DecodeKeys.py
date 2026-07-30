#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING
from typing import Callable
from ...internal.binary.BinaryEncodingMissing import BinaryEncodingMissing

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding


def _decode_keys_recursive(value: object, decode_key: 'Callable[[object], str]') -> object:
    value_type = type(value)

    if value_type is dict:
        decoded: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is str:
                decoded_key = key
            else:
                decoded_key = decode_key(key)
            decoded[decoded_key] = _decode_keys_recursive(item, decode_key)
        return decoded
    if value_type is list:
        return [_decode_keys_recursive(item, decode_key) for item in value]
    return value


def decode_keys(given: object, binary_encoder: 'BinaryEncoding') -> object:
    decode_table = binary_encoder.decode_table

    def decode_key(key: object) -> str:
        try:
            return decode_table[key]
        except (IndexError, TypeError) as exc:
            raise BinaryEncodingMissing(key) from exc

    if isinstance(given, dict):
        return _decode_keys_recursive(given, decode_key)
    if isinstance(given, list):
        return _decode_keys_recursive(given, decode_key)
    return given
