from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.binary.BinaryEncoding import BinaryEncoding


def decode_body(encoded_message_body: Dict[Any, Any], binary_encoder: 'BinaryEncoding') -> Dict[str, Any]:
    from uapi.internal.binary.DecodeKeys import decode_keys

    return decode_keys(encoded_message_body, binary_encoder)
