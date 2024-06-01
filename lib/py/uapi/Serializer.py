from typing import Any

from uapi.Message import Message
from uapi.Serialization import Serialization
from uapi.internal.DeserializeInternal import deserialize_internal
from uapi.internal.SerializeInternal import serialize_internal
from uapi.internal.binary.BinaryEncoder import BinaryEncoder


class Serializer:
    """
    A serializer that converts a Message to and from a serialized form.
    """

    def __init__(self, serialization_impl: Serialization, binary_encoder: BinaryEncoder):
        self.serialization_impl = serialization_impl
        self.binary_encoder = binary_encoder

    def serialize(self, message: Message) -> bytes:
        """
        Serialize a Message into a byte array.
        """
        return serialize_internal(message, self.binary_encoder, self.serialization_impl)

    def deserialize(self, message_bytes: bytes) -> Message:
        """
        Deserialize a Message from a byte array.
        """
        return deserialize_internal(message_bytes, self.serialization_impl, self.binary_encoder)
