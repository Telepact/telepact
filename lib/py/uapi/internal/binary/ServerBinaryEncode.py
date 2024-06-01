from typing import List, Dict, Any
from uapi.internal.binary import EncodeBody, PackBody
from uapi.internal.binary.BinaryEncoding import BinaryEncoding


def server_binary_encode(message: List[Any], binary_encoder: 'BinaryEncoding') -> List[Any]:
    headers: Dict[str, Any] = message[0]
    message_body: Dict[str, Any] = message[1]
    client_known_binary_checksums: List[int] = headers.pop(
        "_clientKnownBinaryChecksums", None)

    if client_known_binary_checksums is None or binary_encoder.checksum not in client_known_binary_checksums:
        headers["enc_"] = binary_encoder.encode_map

    headers["bin_"] = [binary_encoder.checksum]
    encoded_message_body = EncodeBody.encode_body(message_body, binary_encoder)

    final_encoded_message_body: Dict[Any, Any]
    if headers.get("_pac") is True:
        final_encoded_message_body = PackBody.pack_body(encoded_message_body)
    else:
        final_encoded_message_body = encoded_message_body

    return [headers, final_encoded_message_body]
