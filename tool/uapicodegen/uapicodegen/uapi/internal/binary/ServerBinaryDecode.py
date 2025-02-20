from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding


def server_binary_decode(message: list[object], binary_encoder: 'BinaryEncoding') -> list[object]:
    from ...internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError
    from ...internal.binary.DecodeBody import decode_body
    from ...internal.binary.UnpackBody import unpack_body

    headers = cast(dict[str, object], message[0])
    encoded_message_body = cast(dict[object, object], message[1])
    client_known_binary_checksums = cast(list[int], headers.get("bin_", []))
    binary_checksum_used_by_client_on_this_message = cast(
        int, client_known_binary_checksums[0])

    if binary_checksum_used_by_client_on_this_message != binary_encoder.checksum:
        raise BinaryEncoderUnavailableError()

    final_encoded_message_body: dict[object, object]
    if headers.get("pac_") is True:
        final_encoded_message_body = unpack_body(encoded_message_body)
    else:
        final_encoded_message_body = encoded_message_body

    message_body: dict[str, object] = decode_body(
        final_encoded_message_body, binary_encoder)
    return [headers, message_body]
