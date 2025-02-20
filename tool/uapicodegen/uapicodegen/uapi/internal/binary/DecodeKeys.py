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
