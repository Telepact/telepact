#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING

from ..internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError
from ..SerializationError import SerializationError

if TYPE_CHECKING:
    from ..Serialization import Serialization
    from ..Message import Message
    from ..internal.binary.BinaryEncoder import BinaryEncoder
    from ..internal.binary.Base64Encoder import Base64Encoder

def serialize_internal(message: 'Message', binary_encoder: 'BinaryEncoder',
                       base64_encoder: 'Base64Encoder',
                       serializer: 'Serialization') -> bytes:
    headers: dict[str, object] = message.headers

    serialize_as_binary: bool
    if "@binary_" in headers:
        serialize_as_binary = headers.pop("@binary_") is True
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
                base_64_encoded_message = base64_encoder.encode(message_as_pseudo_json)
                return serializer.to_json(base_64_encoded_message)
        else:
            base_64_encoded_message = base64_encoder.encode(message_as_pseudo_json)
            return serializer.to_json(base_64_encoded_message)
    except Exception as e:
        context = (
            "encoding Telepact message as binary or JSON fallback"
            if serialize_as_binary
            else "encoding Telepact message as JSON"
        )
        raise SerializationError(context=context, cause=e) from e
