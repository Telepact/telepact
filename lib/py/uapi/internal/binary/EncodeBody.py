from typing import Any, Dict
from uapi.internal.binary.EncodeKeys import encode_keys
from uapi.internal.binary.BinaryEncoder import BinaryEncoder


def encode_body(message_body: Dict[str, Any], binary_encoder: 'BinaryEncoder') -> Dict[Any, Any]:
    return encode_keys(message_body, binary_encoder)
