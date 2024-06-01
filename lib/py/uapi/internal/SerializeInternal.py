from typing import List, Dict, Any, Union

from uapi import Serialization, SerializationError
from uapi.Message import Message
from uapi.internal.binary.BinaryEncoder import BinaryEncoder
from uapi.internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError


def serialize_internal(message: 'Message', binary_encoder: 'BinaryEncoder',
                       serializer: 'Serialization') -> bytes:
    headers: Dict[str, Any] = message.header

    serialize_as_binary: bool
    if "_binary" in headers:
        serialize_as_binary = headers.pop("_binary") is True
    else:
        serialize_as_binary = False

    message_as_pseudo_json: List[Union[Dict[str, Any], Any]] = [
        message.header, message.body]

    try:
        if serialize_as_binary:
            try:
                encoded_message = binary_encoder.encode(message_as_pseudo_json)
                return serializer.to_msg_pack(encoded_message)
            except BinaryEncoderUnavailableError:
                # We can still submit as json
                return serializer.to_json(message_as_pseudo_json)
        else:
            return serializer.to_json(message_as_pseudo_json)
    except Exception as e:
        raise SerializationError(e)
