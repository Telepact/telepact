from typing import TYPE_CHECKING

from uapi.internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError
from uapi.SerializationError import SerializationError

if TYPE_CHECKING:
    from uapi.Serialization import Serialization
    from uapi.Message import Message
    from uapi.internal.binary.BinaryEncoder import BinaryEncoder


def serialize_internal(message: 'Message', binary_encoder: 'BinaryEncoder',
                       serializer: 'Serialization') -> bytes:
    headers: dict[str, object] = message.headers

    serialize_as_binary: bool
    if "_binary" in headers:
        serialize_as_binary = headers.pop("_binary") is True
    else:
        serialize_as_binary = False

    message_as_pseudo_json: list[object] = [
        message.headers, message.body]

    try:
        if serialize_as_binary:
            try:
                encoded_message = binary_encoder.encode(message_as_pseudo_json)
                return serializer.to_msgpack(encoded_message)
            except BinaryEncoderUnavailableError:
                # We can still submit as json
                return serializer.to_json(message_as_pseudo_json)
        else:
            return serializer.to_json(message_as_pseudo_json)
    except Exception as e:
        raise SerializationError() from e
