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

from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from .ClientBinaryStrategy import ClientBinaryStrategy
    from .BinaryEncodingCache import BinaryEncodingCache


def client_binary_decode_msgpack(message_bytes: bytes, binary_encoding_cache: 'BinaryEncodingCache',
                                 binary_checksum_strategy: 'ClientBinaryStrategy',
                                 serializer: object) -> list[object]:
    headers, body_offset = serializer.from_msgpack_headers(message_bytes)
    binary_checksums = cast(list[int], headers.get("@bin_", []))
    binary_checksum = binary_checksums[0]

    if "@enc_" in headers:
        binary_encoding = cast(dict[str, int], headers["@enc_"])
        binary_encoding_cache.add(binary_checksum, binary_encoding)

    binary_checksum_strategy.update_checksum(binary_checksum)
    new_current_checksum_strategy = binary_checksum_strategy.get_current_checksums()

    binary_encoder = binary_encoding_cache.get(new_current_checksum_strategy[0])

    message_body = serializer.from_msgpack_body(message_bytes, body_offset, binary_encoder)
    return [headers, message_body]
