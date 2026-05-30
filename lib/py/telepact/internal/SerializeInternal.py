#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
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

    has_binary_hint = "@binary_" in headers
    serialize_as_binary = headers.get("@binary_") is True if has_binary_hint else False
    message_headers = headers
    if has_binary_hint:
        message_headers = {
            key: value
            for key, value in headers.items()
            if key != "@binary_"
        }

    message_as_pseudo_json: list[object] = [
        message_headers, message.body]

    try:
        if serialize_as_binary:
            try:
                if hasattr(binary_encoder, "encode_msgpack"):
                    return binary_encoder.encode_msgpack(message_as_pseudo_json, serializer)
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
