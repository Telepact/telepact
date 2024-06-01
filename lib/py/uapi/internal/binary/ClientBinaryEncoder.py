from typing import List
from collections import defaultdict
from uapi.ClientBinaryStrategy import ClientBinaryStrategy
from uapi.internal.binary.BinaryEncoder import BinaryEncoder
from uapi.internal.binary.BinaryEncoding import BinaryEncoding
from uapi.internal.binary.ClientBinaryDecode import client_binary_decode
from uapi.internal.binary.ClientBinaryEncode import client_binary_encode


class ClientBinaryEncoder('BinaryEncoder'):
    def __init__(self, binaryChecksumStrategy: 'ClientBinaryStrategy'):
        self.recentBinaryEncoders = defaultdict(BinaryEncoding)
        self.binaryChecksumStrategy = binaryChecksumStrategy

    def encode(self, message: List[object]) -> List[object]:
        return client_binary_encode(message, self.recentBinaryEncoders, self.binaryChecksumStrategy)

    def decode(self, message: List[object]) -> List[object]:
        return client_binary_decode(message, self.recentBinaryEncoders, self.binaryChecksumStrategy)
