#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING

from ...internal.binary.BinaryEncoder import BinaryEncoder

if TYPE_CHECKING:
    from .BinaryEncodingCache import BinaryEncodingCache

class ClientBinaryEncoder(BinaryEncoder):

    def __init__(self, binary_encoding_cache: 'BinaryEncodingCache') -> None:
        from .ClientBinaryStrategy import ClientBinaryStrategy
        self.binary_encoding_cache = binary_encoding_cache
        self.binaryChecksumStrategy = ClientBinaryStrategy(binary_encoding_cache)

    def encode(self, message: list[object]) -> list[object]:
        from ...internal.binary.ClientBinaryEncode import client_binary_encode
        return client_binary_encode(message, self.binary_encoding_cache, self.binaryChecksumStrategy)

    def decode(self, message: list[object]) -> list[object]:
        from ...internal.binary.ClientBinaryDecode import client_binary_decode
        return client_binary_decode(message, self.binary_encoding_cache, self.binaryChecksumStrategy)