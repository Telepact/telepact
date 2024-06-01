from typing import List, Dict, Any, Union
from uapi.ClientBinaryStrategy import ClientBinaryStrategy
from uapi.internal.binary.BinaryEncoding import BinaryEncoding
from uapi.internal.binary.DecodeBody import decode_body
from uapi.internal.binary.UnpackBody import unpack_body


def client_binary_decode(message: List[Any], recent_binary_encoders: Dict[int, 'BinaryEncoding'],
                         binary_checksum_strategy: 'ClientBinaryStrategy') -> List[Any]:
    headers = message[0]
    encoded_message_body = message[1]
    binary_checksums = headers.get("bin_", [])
    binary_checksum = binary_checksums[0] if binary_checksums else None

    # If there is a binary encoding included on this message, cache it
    if "enc_" in headers:
        binary_encoding = headers["enc_"]
        new_binary_encoder = BinaryEncoding(binary_encoding, binary_checksum)

        recent_binary_encoders[binary_checksum] = new_binary_encoder

    binary_checksum_strategy.update(binary_checksum)
    new_current_checksum_strategy = binary_checksum_strategy.get_current_checksums()

    for key in list(recent_binary_encoders.keys()):
        if key not in new_current_checksum_strategy:
            del recent_binary_encoders[key]

    binary_encoder = recent_binary_encoders.get(binary_checksum)

    final_encoded_message_body = unpack_body(
        encoded_message_body) if headers.get("_pac") else encoded_message_body

    message_body = decode_body(final_encoded_message_body, binary_encoder)
    return [headers, message_body]
