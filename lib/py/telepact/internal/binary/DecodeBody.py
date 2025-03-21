from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding


def decode_body(encoded_message_body: dict[object, object], binary_encoder: 'BinaryEncoding') -> dict[str, object]:
    from ...internal.binary.DecodeKeys import decode_keys

    return cast(dict[str, object], decode_keys(encoded_message_body, binary_encoder))
