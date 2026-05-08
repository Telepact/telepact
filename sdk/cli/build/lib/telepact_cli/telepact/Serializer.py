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

from .Message import Message
from .Serialization import Serialization
from .internal.binary.BinaryEncoder import BinaryEncoder
from .internal.binary.Base64Encoder import Base64Encoder


class Serializer:
    """
    A serializer that converts a Message to and from a serialized form.
    """

    def __init__(self, serialization_impl: Serialization, binary_encoder: BinaryEncoder, base64_encoder: 'Base64Encoder'):
        self.serialization_impl = serialization_impl
        self.binary_encoder = binary_encoder
        self.base64_encoder = base64_encoder

    def serialize(self, message: Message) -> bytes:
        """
        Serialize a Message into a byte array.
        """
        from .internal.SerializeInternal import serialize_internal
        return serialize_internal(message, self.binary_encoder, self.base64_encoder, self.serialization_impl)

    def deserialize(self, message_bytes: bytes) -> Message:
        """
        Deserialize a Message from a byte array.
        """
        from .internal.DeserializeInternal import deserialize_internal
        return deserialize_internal(message_bytes, self.serialization_impl, self.binary_encoder, self.base64_encoder)
