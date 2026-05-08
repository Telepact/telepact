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
