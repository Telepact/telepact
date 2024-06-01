from typing import Any, Dict, List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.binary.BinaryEncoding import BinaryEncoding


def encode_keys(given: Any, binary_encoding: 'BinaryEncoding') -> Any:
    if given is None:
        return given
    elif isinstance(given, dict):
        new_dict: Dict[Any, Any] = {}

        for key, value in given.items():
            final_key = binary_encoding.encode_map.get(key, key)
            encoded_value = encode_keys(value, binary_encoding)

            new_dict[final_key] = encoded_value

        return new_dict
    elif isinstance(given, list):
        return [encode_keys(item, binary_encoding) for item in given]
    else:
        return given
