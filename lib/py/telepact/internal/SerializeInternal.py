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
