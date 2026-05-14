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


def client_binary_decode(message: list[object], binary_encoding_cache: 'BinaryEncodingCache',
                          binary_checksum_strategy: 'ClientBinaryStrategy',
                          ) -> list[object]:
    from ...internal.binary.BinaryPlan import decode_response_body

    headers = cast(dict[str, object], message[0])
    encoded_message_body = cast(dict[object, object], message[1])
    binary_checksums = cast(list[int], headers.get("@bin_", []))
    binary_checksum = binary_checksums[0]

    enc_header = cast(dict[str, object] | None, headers.get("@enc_"))
    if enc_header and "k" in enc_header:
        binary_encoding_cache.add(binary_checksum, enc_header)

    binary_checksum_strategy.update_checksum(binary_checksum)
    new_current_checksum_strategy = binary_checksum_strategy.get_current_checksums()

    binary_encoder = binary_encoding_cache.get(new_current_checksum_strategy[0])
    function_id = cast(int | None, enc_header.get("p") if enc_header else None)
    message_body = decode_response_body(encoded_message_body, binary_encoder, function_id, headers.get("@pac_") is True)
    return [headers, message_body]
