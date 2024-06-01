from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.internal.binary import BinaryEncoding


def server_binary_decode(message: List[Any], binary_encoder: 'BinaryEncoding') -> List[Any]:
    from uapi.internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError
    from uapi.internal.binary.DecodeBody import decode_body
    from uapi.internal.binary.UnpackBody import unpack_body

    headers: Dict[str, Any] = message[0]
    encoded_message_body: Dict[Any, Any] = message[1]
    client_known_binary_checksums: List[int] = headers.get("bin_", [])
    binary_checksum_used_by_client_on_this_message: int = client_known_binary_checksums[0]

    if binary_checksum_used_by_client_on_this_message != binary_encoder.checksum:
        raise BinaryEncoderUnavailableError()

    final_encoded_message_body: Dict[Any, Any]
    if headers.get("_pac") is True:
        final_encoded_message_body = unpack_body(encoded_message_body)
    else:
        final_encoded_message_body = encoded_message_body

    message_body: Dict[str, Any] = decode_body(
        final_encoded_message_body, binary_encoder)
    return [headers, message_body]
