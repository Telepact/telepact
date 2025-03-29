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