#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import TYPE_CHECKING

from ...internal.binary.Base64Encoder import Base64Encoder

if TYPE_CHECKING:
    from .BinaryEncodingCache import BinaryEncodingCache

class ServerBase64Encoder(Base64Encoder):

    def decode(self, message: list[object]) -> list[object]:
        # Server manually runs its decode logic after validation
        return message
    
    def encode(self, message: list[object]) -> list[object]:
        from ...internal.binary.ServerBase64Encode import server_base64_encode
        server_base64_encode(message)
        return message
