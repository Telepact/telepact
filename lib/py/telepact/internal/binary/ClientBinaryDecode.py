#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from .ClientBinaryStrategy import ClientBinaryStrategy
    from .BinaryEncodingCache import BinaryEncodingCache


def client_binary_decode(message: list[object], binary_encoding_cache: 'BinaryEncodingCache',
                         binary_checksum_strategy: 'ClientBinaryStrategy',
                         ) -> list[object]:
    from ...internal.binary.DecodeBody import decode_body
    from ...internal.binary.UnpackBody import unpack_body

    headers = cast(dict[str, object], message[0])
    encoded_message_body = cast(dict[object, object], message[1])
    binary_checksums = cast(list[int], headers.get("@bin_", []))
    binary_checksum = binary_checksums[0]

    # If there is a binary encoding included on this message, cache it
    if "@enc_" in headers:
        binary_encoding = cast(dict[str, int], headers["@enc_"])
        binary_encoding_cache.add(binary_checksum, binary_encoding)

    binary_checksum_strategy.update_checksum(binary_checksum)
    new_current_checksum_strategy = binary_checksum_strategy.get_current_checksums()

    binary_encoder = binary_encoding_cache.get(new_current_checksum_strategy[0])

    final_encoded_message_body: dict[object, object]
    if headers.get("@pac_") is True:
        final_encoded_message_body = unpack_body(encoded_message_body)
    else:
        final_encoded_message_body = encoded_message_body

    message_body = decode_body(final_encoded_message_body, binary_encoder)
    return [headers, message_body]
