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

from typing import Callable, TYPE_CHECKING, Awaitable, NamedTuple

from .DefaultSerialization import DefaultSerialization
from .Serializer import Serializer
from .internal.binary.ServerBinaryEncoder import ServerBinaryEncoder
from .internal.binary.ServerBase64Encoder import ServerBase64Encoder

if TYPE_CHECKING:
    from .Message import Message
    from .TelepactSchema import TelepactSchema
    from .Response import Response

class Server:
    """
    A telepact Server.
    """
    class Options:
        """
        Options for the Server.
        """

        def __init__(self) -> None:
            self.on_error = lambda e: None
            self.on_request = lambda m: None
            self.on_response = lambda m: None
            self.auth_required = True
            self.serialization = DefaultSerialization()

    def __init__(self, telepact_schema: 'TelepactSchema', handler: Callable[['Message'], Awaitable['Message']], options: Options):
        """
        Create a server with the given telepact schema and handler.
        """
        from .internal.binary.ConstructBinaryEncoding import construct_binary_encoding

        self.handler = handler
        self.on_error = options.on_error
        self.on_request = options.on_request
        self.on_response = options.on_response

        self.telepact_schema = telepact_schema

        binary_encoding = construct_binary_encoding(self.telepact_schema)
        binary_encoder = ServerBinaryEncoder(binary_encoding)
        base64_encoder = ServerBase64Encoder()
        self.serializer = Serializer(options.serialization, binary_encoder, base64_encoder)

        if "struct.Auth_" not in self.telepact_schema.parsed and options.auth_required:
            raise RuntimeError(
                "Unauthenticated server. Either define a `struct.Auth_` in your schema or set `options.auth_required` to `false`."
            )

    async def process(self, request_message_bytes: bytes, override_headers: dict[str, object] = {}) -> 'Response':
        """
        Process a given telepact Request Message into a telepact Response Message.
        """
        from .internal.ProcessBytes import process_bytes

        return await process_bytes(request_message_bytes, override_headers, self.serializer, self.telepact_schema, self.on_error,
                                   self.on_request, self.on_response, self.handler)
