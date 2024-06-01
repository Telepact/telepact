from typing import Any, Dict
from uapi.internal.binary.DecodeKeys import decode_keys
from uapi.internal.binary.BinaryEncoding import BinaryEncoding


def decode_body(encoded_message_body: Dict[Any, Any], binary_encoder: 'BinaryEncoding') -> Dict[str, Any]:
    return decode_keys(encoded_message_body, binary_encoder)
