from typing import Any, Dict, List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.binary.BinaryEncoding import BinaryEncoding


def decode_keys(given: Any, binary_encoder: 'BinaryEncoding') -> Any:
    from uapi.internal.binary.BinaryEncodingMissing import BinaryEncodingMissing

    if isinstance(given, dict):
        new_dict: Dict[str, Any] = {}

        for key, value in given.items():
            if isinstance(key, str):
                new_key = key
            else:
                new_key = binary_encoder.decode_map.get(key)

                if new_key is None:
                    raise BinaryEncodingMissing(key)

            encoded_value = decode_keys(value, binary_encoder)
            new_dict[new_key] = encoded_value

        return new_dict
    elif isinstance(given, list):
        return [decode_keys(item, binary_encoder) for item in given]
    else:
        return given
