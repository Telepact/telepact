from typing import cast, TYPE_CHECKING
from ...internal.binary.BinaryEncoding import BinaryEncoding

if TYPE_CHECKING:
    from ...ClientBinaryStrategy import ClientBinaryStrategy


def client_binary_decode(message: list[object], recent_binary_encoders: dict[int, 'BinaryEncoding'],
                         binary_checksum_strategy: 'ClientBinaryStrategy') -> list[object]:
    from ...internal.binary.DecodeBody import decode_body
    from ...internal.binary.UnpackBody import unpack_body

    headers = cast(dict[str, object], message[0])
    encoded_message_body = cast(dict[object, object], message[1])
    binary_checksums = cast(list[int], headers.get("bin_", []))
    binary_checksum = binary_checksums[0]

    # If there is a binary encoding included on this message, cache it
    if "enc_" in headers:
        binary_encoding = cast(dict[str, int], headers["enc_"])
        new_binary_encoder = BinaryEncoding(binary_encoding, binary_checksum)

        recent_binary_encoders[binary_checksum] = new_binary_encoder

    binary_checksum_strategy.update_checksum(binary_checksum)
    new_current_checksum_strategy = binary_checksum_strategy.get_current_checksums()

    for key in list(recent_binary_encoders.keys()):
        if key not in new_current_checksum_strategy:
            del recent_binary_encoders[key]

    binary_encoder = recent_binary_encoders[binary_checksum]

    final_encoded_message_body: dict[object, object]
    if headers.get("pac_") is True:
        final_encoded_message_body = unpack_body(encoded_message_body)
    else:
        final_encoded_message_body = encoded_message_body

    message_body = decode_body(final_encoded_message_body, binary_encoder)
    return [headers, message_body]
