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

from typing import TYPE_CHECKING, cast
from ...internal.binary.BinaryEncoder import PreparedBinaryMessage

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding


def server_binary_encode(message: list[object], binary_encoder: 'BinaryEncoding') -> PreparedBinaryMessage:
    from ...internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError

    headers = cast(dict[str, object], message[0])
    message_body = cast(dict[str, object], message[1])
    function_name = cast(str | None, headers.pop("@fn_", None))
    client_known_binary_checksums = cast(list[int], headers.pop(
        "@clientKnownBinaryChecksums_", None))

    result_tag = list(message_body.keys())[0]

    if result_tag != 'Ok_':
        raise BinaryEncoderUnavailableError()

    if client_known_binary_checksums is None or binary_encoder.checksum not in client_known_binary_checksums:
        headers["@enc_"] = binary_encoder.encode_map
        headers["@encp_"] = binary_encoder.pack_site_tree

    headers["@bin_"] = [binary_encoder.checksum]
    if function_name is not None:
        headers["@fn_"] = function_name
    return PreparedBinaryMessage(headers, message_body, binary_encoder, headers.get("@pac_") is True)
