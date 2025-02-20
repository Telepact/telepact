from typing import cast, TYPE_CHECKING
from ...internal.binary.BinaryEncoding import BinaryEncoding
from ...internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError

if TYPE_CHECKING:
    from ...ClientBinaryStrategy import ClientBinaryStrategy


def client_binary_encode(message: list[object], recent_binary_encoders: dict[int, 'BinaryEncoding'],
                         binary_checksum_strategy: 'ClientBinaryStrategy') -> list[object]:
    from ...internal.binary.EncodeBody import encode_body
    from ...internal.binary.PackBody import pack_body

    headers = cast(dict[str, object], message[0])
    message_body = cast(dict[str, object], message[1])
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
        "pac_") == True else encoded_message_body

    return [headers, final_encoded_message_body]
