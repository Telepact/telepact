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
