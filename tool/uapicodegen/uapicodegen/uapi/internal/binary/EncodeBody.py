from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding


def encode_body(message_body: dict[str, object], binary_encoding: 'BinaryEncoding') -> dict[object, object]:
    from ...internal.binary.EncodeKeys import encode_keys

    return cast(dict[object, object], encode_keys(message_body, binary_encoding))
