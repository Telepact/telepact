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

if TYPE_CHECKING:
    from ...internal.binary.BinaryEncoding import BinaryEncoding


def server_binary_decode(message, serializer, binary_encoder: 'BinaryEncoding') -> list[object]:
    from ...internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError

    headers = cast(dict[str, object], message.headers)
    client_known_binary_checksums = cast(list[int], headers.get("@bin_", []))
    binary_checksum_used_by_client_on_this_message = cast(
        int, client_known_binary_checksums[0])

    if binary_checksum_used_by_client_on_this_message != binary_encoder.checksum:
        raise BinaryEncoderUnavailableError()

    message_body = serializer.from_binary_msgpack_body(
        message.body_bytes, binary_encoder, headers.get("@pac_") is True)
    return [headers, message_body]
