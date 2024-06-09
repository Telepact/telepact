from typing import TYPE_CHECKING

from uapi.internal.binary.BinaryEncoder import BinaryEncoder
from uapi.internal.binary.BinaryEncoding import BinaryEncoding

if TYPE_CHECKING:
    from uapi.ClientBinaryStrategy import ClientBinaryStrategy


class ClientBinaryEncoder(BinaryEncoder):

    def __init__(self, binaryChecksumStrategy: 'ClientBinaryStrategy'):
        self.recentBinaryEncoders: dict[int, BinaryEncoding] = {}
        self.binaryChecksumStrategy = binaryChecksumStrategy

    def encode(self, message: list[object]) -> list[object]:
        from uapi.internal.binary.ClientBinaryEncode import client_binary_encode
        return client_binary_encode(message, self.recentBinaryEncoders, self.binaryChecksumStrategy)

    def decode(self, message: list[object]) -> list[object]:
        from uapi.internal.binary.ClientBinaryDecode import client_binary_decode
        return client_binary_decode(message, self.recentBinaryEncoders, self.binaryChecksumStrategy)
