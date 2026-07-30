#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import cast, TYPE_CHECKING
from ...internal.binary.BinaryEncoding import BinaryEncoding
from ...internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError

if TYPE_CHECKING:
    from .BinaryEncodingCache import BinaryEncodingCache
    from .ClientBinaryStrategy import ClientBinaryStrategy


def client_binary_encode(message: list[object], binary_encoding_cache: 'BinaryEncodingCache',
                         binary_checksum_strategy: 'ClientBinaryStrategy') -> list[object]:
    from ...internal.binary.EncodeBody import encode_body
    from ...internal.binary.PackBody import pack_body

    headers = cast(dict[str, object], message[0])
    message_body = cast(dict[str, object], message[1])
    force_send_json = headers.pop("_forceSendJson", None)

    checksums = binary_checksum_strategy.get_current_checksums()
    headers["@bin_"] = checksums

    if force_send_json == True:
        raise BinaryEncoderUnavailableError()
    
    if len(checksums) > 1:
        raise BinaryEncoderUnavailableError()
    
    binary_encoding = binary_encoding_cache.get(checksums[0]) if checksums else None

    if not binary_encoding:
        raise BinaryEncoderUnavailableError()

    encoded_message_body = encode_body(message_body, binary_encoding)

    final_encoded_message_body = pack_body(encoded_message_body) if headers.get(
        "@pac_") == True else encoded_message_body

    return [headers, final_encoded_message_body]
