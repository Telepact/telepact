#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING

from ...internal.binary.Base64Encoder import Base64Encoder

if TYPE_CHECKING:
    from .BinaryEncodingCache import BinaryEncodingCache

class ClientBase64Encoder(Base64Encoder):

    def decode(self, message: list[object]) -> list[object]:
        from ...internal.binary.ClientBase64Decode import client_base64_decode
        client_base64_decode(message)
        return message
    
    def encode(self, message: list[object]) -> list[object]:
        from ...internal.binary.ClientBase64Encode import client_base64_encode
        client_base64_encode(message)
        return message
