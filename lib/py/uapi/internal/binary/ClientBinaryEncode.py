from typing import List, Dict, Optional
from uapi.ClientBinaryStrategy import ClientBinaryStrategy
from uapi.internal.binary.BinaryEncoding import BinaryEncoding
from uapi.internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError
from uapi.internal.binary.EncodeBody import encode_body
from uapi.internal.binary.PackBody import pack_body


def client_binary_encode(message: List[object], recent_binary_encoders: Dict[int, 'BinaryEncoding'],
                         binary_checksum_strategy: 'ClientBinaryStrategy') -> List[object]:
    headers = message[0]
    message_body = message[1]
    force_send_json = headers.pop("_forceSendJson", None)

    headers["bin_"] = binary_checksum_strategy.get_current_checksums()

    if force_send_json == True:
        raise BinaryEncoderUnavailableError()

    if len(recent_binary_encoders) > 1:
        raise BinaryEncoderUnavailableError()

    binary_encoder_optional = next(iter(recent_binary_encoders.values()), None)
    if not binary_encoder_optional:
        raise BinaryEncoderUnavailableError()
    binary_encoder = binary_encoder_optional

    encoded_message_body = encode_body(message_body, binary_encoder)

    final_encoded_message_body = pack_body(encoded_message_body) if headers.get(
        "_pac") == True else encoded_message_body

    return [headers, final_encoded_message_body]
