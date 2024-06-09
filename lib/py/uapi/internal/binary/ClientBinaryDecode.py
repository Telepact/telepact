from typing import cast, TYPE_CHECKING
from uapi.internal.binary.BinaryEncoding import BinaryEncoding

if TYPE_CHECKING:
    from uapi.ClientBinaryStrategy import ClientBinaryStrategy


def client_binary_decode(message: list[object], recent_binary_encoders: dict[int, 'BinaryEncoding'],
                         binary_checksum_strategy: 'ClientBinaryStrategy') -> list[object]:
    from uapi.internal.binary.DecodeBody import decode_body
    from uapi.internal.binary.UnpackBody import unpack_body

    headers = cast(dict[str, object], message[0])
    encoded_message_body = cast(dict[str, object], message[1])
    binary_checksums: list[int] = cast(list[int], headers["bin_"])
    binary_checksum: int = binary_checksums[0]

    # If there is a binary encoding included on this message, cache it
    if "enc_" in headers:
        binary_encoding = cast(dict[str, int], headers["enc_"])
        new_binary_encoder = BinaryEncoding(binary_encoding, binary_checksum)

        recent_binary_encoders[binary_checksum] = new_binary_encoder

    binary_encoder: BinaryEncoding = recent_binary_encoders[binary_checksum]

    final_encoded_message_body = unpack_body(
        encoded_message_body) if headers.get("_pac") else encoded_message_body

    message_body = decode_body(final_encoded_message_body, binary_encoder)
    return [headers, message_body]
