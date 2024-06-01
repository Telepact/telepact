from typing import Any, Dict, List, Union

from uapi.internal.binary.BinaryEncoding import BinaryEncoding
from uapi.internal.binary.BinaryEncodingMissing import BinaryEncodingMissing


def decode_keys(given: Any, binary_encoder: 'BinaryEncoding') -> Any:
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
