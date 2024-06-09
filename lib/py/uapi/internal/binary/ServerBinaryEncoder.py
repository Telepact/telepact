from typing import list, TYPE_CHECKING


if TYPE_CHECKING:
    from uapi.internal.binary.BinaryEncoding import BinaryEncoding


class ServerBinaryEncoder:
    def __init__(self, binary_encoder: 'BinaryEncoding'):
        self.binary_encoder = binary_encoder

    def encode(self, message: list[object]) -> list[object]:
        from uapi.internal.binary.ServerBinaryEncode import server_binary_encode
        return server_binary_encode(message, self.binary_encoder)

    def decode(self, message: list[object]) -> list[object]:
        from uapi.internal.binary.ServerBinaryDecode import server_binary_decode
        return server_binary_decode(message, self.binary_encoder)
