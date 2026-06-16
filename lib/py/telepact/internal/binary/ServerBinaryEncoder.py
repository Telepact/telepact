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
    from ...internal.binary.BinaryEncoding import BinaryEncoding


class ServerBinaryEncoder(BinaryEncoder):
    def __init__(self, binary_encoder: 'BinaryEncoding'):
        self.binary_encoder = binary_encoder

    def encode_msgpack(self, message: list[object], serializer: object) -> bytes:
        from ...internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError

        input_headers = message[0]
        body = message[1]
        client_known_binary_checksums = input_headers.pop("@clientKnownBinaryChecksums_", None)
        headers = {
            key: value
            for key, value in input_headers.items()
        }

        if "Ok_" not in body:
            raise BinaryEncoderUnavailableError()

        if client_known_binary_checksums is None or self.binary_encoder.checksum not in client_known_binary_checksums:
            headers["@enc_"] = self.binary_encoder.encode_map

        headers["@bin_"] = [self.binary_encoder.checksum]
        return serializer.to_binary_msgpack(headers, body, self.binary_encoder)

    def decode_msgpack(self, message_bytes: bytes, serializer: object) -> list[object]:
        from ...internal.binary.ServerBinaryDecode import server_binary_decode_msgpack
        return server_binary_decode_msgpack(message_bytes, self.binary_encoder, serializer)
