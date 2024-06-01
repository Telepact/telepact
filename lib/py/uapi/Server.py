from typing import Callable, Dict, Any
from uapi.internal.binary import ServerBinaryEncoder
from uapi.internal import process_bytes, construct_binary_encoding, extend_u_api_schema, get_internal_u_api_json
from uapi.internal.types import USelect, UStruct, UType
from uapi import Message, UApiSchema, Serializer, DefaultSerialization


class Server:
    """
    A uAPI Server.
    """
    class Options:
        """
        Options for the Server.
        """

        def __init__(self):
            self.on_error = lambda e: None
            self.on_request = lambda m: None
            self.on_response = lambda m: None
            self.auth_required = True
            self.serialization = DefaultSerialization()

    def __init__(self, u_api_schema: UApiSchema, handler: Callable[[Message], Message], options: Options):
        """
        Create a server with the given uAPI schema and handler.
        """
        self.handler = handler
        self.on_error = options.on_error
        self.on_request = options.on_request
        self.on_response = options.on_response

        parsed_types: Dict[str, UType] = {}
        type_extensions: Dict[str, UType] = {
            "_ext.Select_": USelect(parsed_types)}

        self.u_api_schema = extend_u_api_schema(
            u_api_schema, get_internal_u_api_json(), type_extensions)

        parsed_types.update(self.u_api_schema.parsed)

        binary_encoding = construct_binary_encoding(self.u_api_schema)
        binary_encoder = ServerBinaryEncoder(binary_encoding)
        self.serializer = Serializer(options.serialization, binary_encoder)

        if len(self.u_api_schema.parsed.get("struct.Auth_").fields) == 0 and options.auth_required:
            raise RuntimeError(
                "Unauthenticated server. Either define a non-empty `struct._Auth` in your schema or set `options.auth_required` to `false`."
            )

    def process(self, request_message_bytes: bytes) -> bytes:
        """
        Process a given uAPI Request Message into a uAPI Response Message.
        """
        return process_bytes(request_message_bytes, self.serializer, self.u_api_schema, self.on_error,
                             self.on_request, self.on_response, self.handler)
