from typing import Callable, TYPE_CHECKING, Awaitable

from .DefaultSerialization import DefaultSerialization
from .Serializer import Serializer
from .internal.binary.ServerBinaryEncoder import ServerBinaryEncoder

if TYPE_CHECKING:
    from .Message import Message
    from .UApiSchema import UApiSchema


class Server:
    """
    A uAPI Server.
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

    def __init__(self, u_api_schema: 'UApiSchema', handler: Callable[['Message'], Awaitable['Message']], options: Options):
        """
        Create a server with the given uAPI schema and handler.
        """
        from .internal.binary.ConstructBinaryEncoding import construct_binary_encoding

        self.handler = handler
        self.on_error = options.on_error
        self.on_request = options.on_request
        self.on_response = options.on_response

        self.u_api_schema = u_api_schema

        binary_encoding = construct_binary_encoding(self.u_api_schema)
        binary_encoder = ServerBinaryEncoder(binary_encoding)
        self.serializer = Serializer(options.serialization, binary_encoder)

        if "struct.Auth_" not in self.u_api_schema.parsed and options.auth_required:
            raise RuntimeError(
                "Unauthenticated server. Either define a `struct.Auth_` in your schema or set `options.auth_required` to `false`."
            )

    async def process(self, request_message_bytes: bytes) -> bytes:
        """
        Process a given uAPI Request Message into a uAPI Response Message.
        """
        from .internal.ProcessBytes import process_bytes

        return await process_bytes(request_message_bytes, self.serializer, self.u_api_schema, self.on_error,
                                   self.on_request, self.on_response, self.handler)
