from __future__ import annotations
import uapi
import uapi._random_generator as _rg
import uapi._util as _util
import uapi._util_types as _types
from typing import Coroutine, List, Dict, Any, Callable, Optional, Union, Tuple, Type
from concurrent.futures import Future


class Client:
    """
    A uAPI client.
    """

    class Options:
        """
        Options for the Client.
        """

        def __init__(self):
            """
            Initializes Options with default values.
            """
            import uapi._default_serializer as def_ser
            import uapi._default_client_binary_strategy as def_cbin
            self.use_binary: bool = False
            self.timeout_ms_default: int = 5000
            self.serialization_impl: 'SerializationImpl' = def_ser._DefaultSerializer()
            self.binary_strategy: 'ClientBinaryStrategy' = def_cbin._DefaultClientBinaryStrategy()

    def __init__(self, adapter: Callable[[Message, Serializer], Coroutine[Any, Any, Message]], options: Options):
        """
        Create a client with the given transport adapter.

        Example transport adapter:

        adapter = lambda request_message, serializer: Future(() -> (
            request_message_bytes := serializer.serialize(request_message),
            response_message_bytes := YOUR_TRANSPORT.transport(request_message_bytes),
            serializer.deserialize(response_message_bytes)
        ))

        :param adapter: The transport adapter function.
        :param options: Options for the client.
        """
        self.adapter = adapter
        self.use_binary_default = options.use_binary
        self.timeout_ms_default = options.timeout_ms_default
        self.serializer = Serializer(
            options.serialization_impl, _types._ClientBinaryEncoder(options.binary_strategy))

    async def request(self, request_message: Message) -> Message:
        """
        Submit a uAPI Request Message. Returns a uAPI Response Message.

        :param request_message: The uAPI Request Message.
        :return: The uAPI Response Message.
        """
        return await _util.process_request_object(request_message, self.adapter, self.serializer, self.timeout_ms_default,
                                                  self.use_binary_default)


class ClientBinaryStrategy:
    """
    The strategy used by the client to maintain binary encodings compatible with
    the server.
    """

    def update(self, checksum: int) -> None:
        """
        Update the strategy according to a recent binary encoding checksum returned
        by the server.

        :param checksum: The checksum returned by the server.
        """
        pass

    def get_current_checksums(self) -> List[int]:
        """
        Get the current binary encoding strategy as a list of binary encoding
        checksums that should be sent to the server.

        :return: List of checksums.
        """
        pass


class Message:
    """
    A uAPI Message.
    """

    def __init__(self, header: dict[str, Any] = None, body: dict[str, Any] = None):
        self.header: dict[str, Any] = {} if header is None else header.copy()
        self.body: dict[str, Any] = {} if body is None else body.copy()

    def get_body_target(self) -> str:
        """
        Get the target from the body.
        """
        entry: Tuple[str, Any] = _util.union_entry(self.body)
        return entry[0]

    def get_body_payload(self) -> dict[str, Any]:
        """
        Get the payload from the body.
        """
        entry: Tuple[str, Any] = _util.union_entry(self.body)
        return entry[1]

    @classmethod
    def from_target_and_payload(cls, target: str, payload: dict[str, Any]) -> 'Message':
        """
        Create a Message instance from target and payload.
        """
        return cls(header={}, body={target: payload})


class MockServer:
    """
    A Mock instance of a uAPI server.
    """

    class Options:
        """
        Options for the MockServer.
        """

        def __init__(self) -> None:
            self.on_error: Callable[[Exception], None] = lambda e: None
            self.enable_message_response_generation: bool = True
            self.enable_optional_field_generation: bool = True
            self.randomize_optional_field_generation: bool = True
            self.generated_collection_length_min: int = 0
            self.generated_collection_length_max: int = 3

    def __init__(self, u_api_schema: UApiSchema, options: Options) -> None:
        self.random: _rg._RandomGenerator = _rg._RandomGenerator(
            options.generated_collection_length_min, options.generated_collection_length_max)
        self.enableGeneratedDefaultStub: bool = options.enable_message_response_generation
        self.enable_optional_field_generation: bool = options.enable_optional_field_generation
        self.randomize_optional_field_generation: bool = options.randomize_optional_field_generation

        self.stubs: List[_types._MockStub] = []
        self.invocations: List[str] = []

        parsed_types: Dict[str, type] = {}
        type_extensions: Dict[str, type] = {}

        type_extensions["_ext._Call"] = _types._UMockCall(parsed_types)
        type_extensions["_ext._Stub"] = _types._UMockStub(parsed_types)

        combined_u_api_schema: UApiSchema = _util.extend_uapi_schema(
            u_api_schema, _util.get_mock_uapi_json(), type_extensions)

        server_options: Server.Options = Server.Options()
        server_options.on_error = options.on_error
        server_options.auth_required = False

        self.server: Server = Server(
            combined_u_api_schema, self._handle, server_options)

        final_u_api_schema: UApiSchema = self.server.u_api_schema
        final_parsed_u_api_schema: Dict[str, type] = final_u_api_schema.parsed

        parsed_types.update(final_parsed_u_api_schema)

    async def process(self, message: bytes) -> bytes:
        """
        Process a given uAPI Request Message into a uAPI Response Message.

        :param message: The uAPI request message.
        :return: The uAPI response message.
        """
        return await self.server.process(message)

    async def _handle(self, request_message: bytes) -> bytes:
        return await _util.mock_handle(request_message, self.stubs, self.invocations, self.random,
                                       self.server.u_api_schema, self.enableGeneratedDefaultStub,
                                       self.enable_optional_field_generation, self.randomize_optional_field_generation)


class SerializationError(Exception):
    """
    Indicates failure to serialize a uAPI Message.
    """
    pass


class SerializationImpl:
    """
    A serialization implementation that converts between pseudo-JSON Objects and
    byte array JSON payloads.

    Pseudo-JSON objects are defined as data structures that represent JSON
    objects as Maps and JSON arrays as Lists.
    """

    def to_json(self, message: Any) -> bytes:
        """
        Convert the given message to a byte array JSON payload.

        Args:
            message (Any): The message to serialize.

        Returns:
            bytes: The serialized message in byte array JSON payload format.
        Raises:
            Throwable: If an error occurs during serialization.
        """
        raise NotImplementedError

    def to_msgpack(self, message: Any) -> bytes:
        """
        Convert the given message to a byte array using MessagePack format.

        Args:
            message (Any): The message to serialize.

        Returns:
            bytes: The serialized message in MessagePack format.
        Raises:
            Throwable: If an error occurs during serialization.
        """
        raise NotImplementedError

    def from_json(self, bytes: bytes) -> Any:
        """
        Convert the given byte array JSON payload to an object.

        Args:
            bytes (bytes): The byte array JSON payload.

        Returns:
            Any: The deserialized object.
        Raises:
            Throwable: If an error occurs during deserialization.
        """
        raise NotImplementedError

    def from_msgpack(self, bytes: bytes) -> Any:
        """
        Convert the given byte array in MessagePack format to an object.

        Args:
            bytes (bytes): The byte array in MessagePack format.

        Returns:
            Any: The deserialized object.
        Raises:
            Throwable: If an error occurs during deserialization.
        """
        raise NotImplementedError


class Serializer:
    """
    A serializer that converts a Message to and from a serialized form.
    """

    def __init__(self, serialization_impl: 'SerializationImpl', binary_encoder: _types._BinaryEncoder) -> None:
        """
        Initialize Serializer with the provided SerializationImpl and _BinaryEncoder.

        Args:
            serialization_impl (SerializationImpl): The serialization implementation.
            binary_encoder (_BinaryEncoder): The binary encoder.
        """
        self.serialization_impl = serialization_impl
        self.binary_encoder = binary_encoder

    def serialize(self, message: Message) -> bytes:
        """
        Serialize a Message into a byte array.

        Args:
            message (Message): The message to serialize.

        Returns:
            bytes: The serialized message.
        """
        return _util.serialize(message, self.binary_encoder, self.serialization_impl)

    def deserialize(self, message_bytes: bytes) -> Message:
        """
        Deserialize a Message from a byte array.

        Args:
            message_bytes (bytes): The byte array containing the serialized message.

        Returns:
            Message: The deserialized message.
        """
        return _util.deserialize(message_bytes, self.serialization_impl, self.binary_encoder)


class Server:
    """
    A uAPI Server.
    """

    class Options:
        """
        Options for the Server.
        """

        def __init__(self) -> None:
            import uapi._default_serializer as def_ser
            self.on_error: Callable[[Exception], None] = lambda e: None
            self.on_request: Callable[[Message], None] = lambda m: None
            self.on_response: Callable[[Message], None] = lambda m: None
            self.auth_required: bool = True
            self.serializer: 'SerializationImpl' = def_ser._DefaultSerializer()

    def __init__(self, u_api_schema: UApiSchema, handler: Callable[[Message], Coroutine[Any, Any, Message]], options: Options) -> None:
        self.handler: Callable[[Message], Message] = handler
        self.on_error: Callable[[Exception], None] = options.on_error
        self.on_request: Callable[[Message], None] = options.on_request
        self.on_response: Callable[[Message], None] = options.on_response

        parsed_types: Dict[str, _types._UType] = {}
        type_extensions: Dict[str, _types._UType] = {}

        type_extensions['_ext.Select_'] = _types._USelect(parsed_types)

        self.u_api_schema: UApiSchema = _util.extend_uapi_schema(
            u_api_schema, _util.get_internal_uapi_json(), type_extensions)

        parsed_types.update(self.u_api_schema.parsed)

        binary_encoding = _util.construct_binary_encoding(self.u_api_schema)
        binary_encoder = _types._ServerBinaryEncoder(binary_encoding)
        self.serializer: 'SerializationImpl' = Serializer(
            options.serializer, binary_encoder)

        if len(self.u_api_schema.parsed['struct.Auth_'].fields) == 0 and options.auth_required:
            raise Exception(
                'Unauthenticated server. Either define a non-empty `struct._Auth` in your schema or set `options.auth_required` to `False`.')

    async def process(self, request_message_bytes: bytes) -> bytes:
        """
        Process a given uAPI Request Message into a uAPI Response Message.

        Args:
            request_message_bytes (bytes): The request message bytes.

        Returns:
            bytes: The response message bytes.
        """
        return await _util.process_bytes(request_message_bytes, self.serializer, self.u_api_schema, self.on_error, self.on_request, self.on_response, self.handler)


class UApiError(RuntimeError):
    """
    Indicates critical failure in uAPI processing logic.
    """

    def __init__(self, message: str = None, cause: Exception = None):
        """
        Initialize UApiError instance.

        Args:
            message (str): The error message.
            cause (Throwable): The cause of the error.
        """
        super().__init__(message) if not cause else super().__init__(cause)


class UApiSchema:
    """
    A parsed uAPI schema.
    """

    def __init__(self, original: List[object], parsed: Dict[str, _types._UType], parsed_request_headers: Dict[str, _types._UFieldDeclaration], parsed_response_headers: Dict[str, _types._UFieldDeclaration], type_extensions: Dict[str, _types._UType]):
        self.original = original
        self.parsed = parsed
        self.parsed_request_headers = parsed_request_headers
        self.parsed_response_headers = parsed_response_headers
        self.type_extensions = type_extensions

    @staticmethod
    def from_json(json: str) -> 'UApiSchema':
        """
        Create a UApiSchema object from JSON.
        """
        return _util.new_uapi_schema(json, {})

    @staticmethod
    def extend(base: 'UApiSchema', json: str) -> 'UApiSchema':
        """
        Extend a UApiSchema object with JSON.
        """
        return _util.extend_uapi_schema(base, json, {})


class UApiSchemaParseError(RuntimeError):
    """
    Indicates failure to parse a uAPI Schema.
    """

    def __init__(self, schema_parse_failures: List[_types._SchemaParseFailure], cause: Exception = None):
        super().__init__(str(_util.map_schema_parse_failures_to_pseudo_json(schema_parse_failures)))
        self.schema_parse_failures = schema_parse_failures
        self.schema_parse_failures_pseudo_json = _util.map_schema_parse_failures_to_pseudo_json(
            schema_parse_failures)

    @staticmethod
    def map_schema_parse_failures_to_pseudo_json(schema_parse_failures: List[_types._SchemaParseFailure]) -> List[Dict[str, Any]]:
        """
        Map schema parse failures to pseudo JSON format.
        """
        return [{'path': f.path, 'reason': {f.reason: f.data}} for f in schema_parse_failures]
