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

    def encode_msgpack(self, message: list[object], serializer: object) -> bytes:
        from ...internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError

        headers = message[0]
        body = message[1]
        force_send_json = headers.pop("_forceSendJson", None)

        checksums = self.binaryChecksumStrategy.get_current_checksums()
        headers["@bin_"] = checksums

        if force_send_json is True or len(checksums) > 1:
            raise BinaryEncoderUnavailableError()

        binary_encoding = self.binary_encoding_cache.get(checksums[0]) if checksums else None
        if not binary_encoding:
            raise BinaryEncoderUnavailableError()

        return serializer.to_binary_msgpack(headers, body, binary_encoding)

    def decode_msgpack(self, message_bytes: bytes, serializer: object) -> list[object]:
        from ...internal.binary.ClientBinaryDecode import client_binary_decode_msgpack
        return client_binary_decode_msgpack(message_bytes, self.binary_encoding_cache, self.binaryChecksumStrategy, serializer)
