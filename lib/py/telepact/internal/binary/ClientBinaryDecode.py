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
    from contextvars import ContextVar
    from .ClientBinaryStrategy import ClientBinaryStrategy
    from .BinaryEncodingCache import BinaryEncodingCache


def client_binary_decode(message: list[object], binary_encoding_cache: 'BinaryEncodingCache',
                         binary_checksum_strategy: 'ClientBinaryStrategy',
                         current_function_name: 'ContextVar[str | None]',
                         ) -> list[object]:
    from ...DefaultSerialization import DefaultSerialization

    headers = cast(dict[str, object], message[0])
    encoded_message_body = cast(dict[object, object], message[1])
    binary_checksums = cast(list[int], headers.get("@bin_", []))
    binary_checksum = binary_checksums[0]

    # If there is a binary encoding included on this message, cache it
    if "@enc_" in headers:
        binary_encoding = cast(dict[str, int], headers["@enc_"])
        binary_pack_encoding = cast(dict[str, object], headers.get("@encp_", {}))
        binary_encoding_cache.add(binary_checksum, binary_encoding, binary_pack_encoding)

    binary_checksum_strategy.update_checksum(binary_checksum)
    new_current_checksum_strategy = binary_checksum_strategy.get_current_checksums()

    binary_encoder = binary_encoding_cache.get(new_current_checksum_strategy[0])

    pack_tree: dict[str, object] | None = None
    function_name = current_function_name.get()
    if headers.get("@pac_") is True and function_name is not None:
        response_pack_tree = binary_encoder.response_pack_trees.get(function_name)
        if isinstance(response_pack_tree, dict):
            pack_tree = response_pack_tree

    message_body = cast(dict[str, object], DefaultSerialization.decode_binary_body(
        encoded_message_body,
        binary_encoder,
        pack_tree,
    ))
    return [headers, message_body]
