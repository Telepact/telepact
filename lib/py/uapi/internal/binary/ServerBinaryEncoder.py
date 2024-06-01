from typing import List
from uapi.internal.binary.ServerBinaryDecode import server_binary_decode
from uapi.internal.binary.ServerBinaryEncode import server_binary_encode
from uapi.internal.binary.BinaryEncoding import BinaryEncoding


class ServerBinaryEncoder:
    def __init__(self, binary_encoder: BinaryEncoding):
        self.binary_encoder = binary_encoder

    def encode(self, message: List[object]) -> List[object]:
        return server_binary_encode(message, self.binary_encoder)

    def decode(self, message: List[object]) -> List[object]:
        return server_binary_decode(message, self.binary_encoder)
