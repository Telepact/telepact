from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding


def server_binary_encode(message: list[object], binary_encoder: 'BinaryEncoding') -> list[object]:
    from ...internal.binary.EncodeBody import encode_body
    from ...internal.binary.PackBody import pack_body
    from ...internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError

    headers = cast(dict[str, object], message[0])
    message_body = cast(dict[str, object], message[1])
    client_known_binary_checksums = cast(list[int], headers.pop(
        "_clientKnownBinaryChecksums", None))

    result_tag = list(message_body.keys())[0]

    if result_tag != 'Ok_':
        raise BinaryEncoderUnavailableError()

    if client_known_binary_checksums is None or binary_encoder.checksum not in client_known_binary_checksums:
        headers["enc_"] = binary_encoder.encode_map

    headers["bin_"] = [binary_encoder.checksum]
    encoded_message_body = encode_body(message_body, binary_encoder)

    final_encoded_message_body: dict[object, object]
    if headers.get("pac_") is True:
        final_encoded_message_body = pack_body(encoded_message_body)
    else:
        final_encoded_message_body = encoded_message_body

    return [headers, final_encoded_message_body]
