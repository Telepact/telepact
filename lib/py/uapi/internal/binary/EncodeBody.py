from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.binary.BinaryEncoding import BinaryEncoding


def encode_body(message_body: dict[str, object], binary_encoding: 'BinaryEncoding') -> dict[object, object]:
    from uapi.internal.binary.EncodeKeys import encode_keys

    return encode_keys(message_body, binary_encoding)
