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

from typing import TYPE_CHECKING

from ...internal.binary.Base64Encoder import Base64Encoder

if TYPE_CHECKING:
    from .BinaryEncodingCache import BinaryEncodingCache

class ServerBase64Encoder(Base64Encoder):

    def decode(self, message: list[object]) -> list[object]:
        # Server manaully runs it decode logic after validation
        return message
    
    def encode(self, message: list[object]) -> list[object]:
        from ...internal.binary.ServerBase64Encode import server_base64_encode
        server_base64_encode(message)
        return message
