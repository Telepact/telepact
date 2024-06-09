from typing import list, dict, object, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.binary.BinaryEncoding import BinaryEncoding


def server_binary_encode(message: list[object], binary_encoder: 'BinaryEncoding') -> list[object]:
    from uapi.internal.binary.EncodeBody import encode_body
    from uapi.internal.binary.PackBody import pack_body

    headers: dict[str, object] = message[0]
    message_body: dict[str, object] = message[1]
    client_known_binary_checksums: list[int] = headers.pop(
        "_clientKnownBinaryChecksums", None)

    if client_known_binary_checksums is None or binary_encoder.checksum not in client_known_binary_checksums:
        headers["enc_"] = binary_encoder.encode_map

    headers["bin_"] = [binary_encoder.checksum]
    encoded_message_body = encode_body(message_body, binary_encoder)

    final_encoded_message_body: dict[object, object]
    if headers.get("_pac") is True:
        final_encoded_message_body = pack_body(encoded_message_body)
    else:
        final_encoded_message_body = encoded_message_body

    return [headers, final_encoded_message_body]
