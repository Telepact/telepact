from __future__ import annotations
from uapi._util import map_schema_parse_failures_to_pseudo_json
from uapi._util_types import _SchemaParseFailure
from typing import List, Dict, Any
from uapi._util import new_uapi_schema, extend_uapi_schema
from uapi._util import newUApiSchema, extendUApiSchema
from uapi._util_types import _UType
from typing import List, Dict
from uapi._util import _Util, Serializer, _DefaultSerializer, _ServerBinaryEncoder, processBytes, constructBinaryEncoding, getInternalUApiJson
from uapi._util_types import Consumer, SerializationImpl, UApiSchema, Message
from typing import Callable, Optional, Any, Union
from uapi._util_types import Message
from uapi._util import serialize, deserialize
from typing import Any, List, Dict
from uapi._util import RuntimeException
from uapi._util_types import Throwable
from mock_call import MockCall
from mock_stub import MockStub
from random_generator import _RandomGenerator
from uapi_schema import UApiSchema
from server import Server
from uapi._util import mockHandle
from uapi._util_types import Consumer
from typing import Callable, List, Dict
from uapi._util import union_entry
from uapi._util_types import Map
from typing import Any, Dict, Tuple
from concurrent.futures import Future
from typing import Callable, Type

from uapi._util import process_request_object, process_bytes
from uapi._util_types import SerializationImpl, Serializer, ClientBinaryStrategy, Message


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
            self.use_binary: bool = False
            self.timeout_ms_default: int = 5000
            self.serialization_impl: SerializationImpl = _DefaultSerializer()
            self.binary_strategy: ClientBinaryStrategy = _DefaultClientBinaryStrategy()

    def __init__(self, adapter: Callable[[Message, Serializer], Future[Message]], options: Options):
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
            options.serialization_impl, _ClientBinaryEncoder(options.binary_strategy))

    def request(self, request_message: Message) -> Message:
        """
        Submit a uAPI Request Message. Returns a uAPI Response Message.

        :param request_message: The uAPI Request Message.
        :return: The uAPI Response Message.
        """
        return process_request_object(request_message, self.adapter, self.serializer, self.timeout_ms_default,
                                      self.use_binary_default)


class ClientBinaryStrategy:
    """
    The strategy used by the client to maintain binary encodings compatible with
    the server.
    """

    def update(self, checksum: Integer) -> None:
        """
        Update the strategy according to a recent binary encoding checksum returned
        by the server.

        :param checksum: The checksum returned by the server.
        """
        pass

    def get_current_checksums(self) -> List[Integer]:
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

    def __init__(self, header: Map[str, Any] = None, body: Map[str, Any] = None):
        self.header: Map[str, Any] = {} if header is None else header.copy()
        self.body: Map[str, Any] = {} if body is None else body.copy()

    def get_body_target(self) -> str:
        """
        Get the target from the body.
        """
        entry: Tuple[str, Any] = union_entry(self.body)
        return entry[0]

    def get_body_payload(self) -> Map[str, Any]:
        """
        Get the payload from the body.
        """
        entry: Tuple[str, Any] = union_entry(self.body)
        return entry[1]

    @classmethod
    def from_target_and_payload(cls, target: str, payload: Map[str, Any]) -> 'Message':
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
            self.onError: Callable[[Exception], None] = lambda e: None
            self.enableMessageResponseGeneration: bool = True
            self.generatedCollectionLengthMin: int = 0
            self.generatedCollectionLengthMax: int = 3

    def __init__(self, u_api_schema: UApiSchema, options: Options) -> None:
        self.random: _RandomGenerator = _RandomGenerator(
            options.generatedCollectionLengthMin, options.generatedCollectionLengthMax)
        self.enableGeneratedDefaultStub: bool = options.enableMessageResponseGeneration

        self.stubs: List[MockStub] = []
        self.invocations: List[str] = []

        parsed_types: Dict[str, type] = {}
        type_extensions: Dict[str, type] = {}

        type_extensions["_ext._Call"] = MockCall(parsed_types)
        type_extensions["_ext._Stub"] = MockStub(parsed_types)

        combined_u_api_schema: UApiSchema = UApiSchema.extendWithExtensions(
            u_api_schema, _Util.getMockUApiJson(), type_extensions)

        server_options: Server.Options = Server.Options()
        server_options.onError = options.onError

        self.server: Server = Server(
            combined_u_api_schema, self.handle, server_options)

        final_u_api_schema: UApiSchema = self.server.u_api_schema
        final_parsed_u_api_schema: Dict[str, type] = final_u_api_schema.parsed

        parsed_types.update(final_parsed_u_api_schema)

    def process(self, message: bytes) -> bytes:
        """
        Process a given uAPI Request Message into a uAPI Response Message.

        :param message: The uAPI request message.
        :return: The uAPI response message.
        """
        return self.server.process(message)

    def handle(self, request_message: bytes) -> bytes:
        """
        Handle the uAPI request message.

        :param request_message: The uAPI request message.
        :return: The uAPI response message.
        """
        return mockHandle(request_message, self.stubs, self.invocations, self.random,
                          self.server.u_api_schema, self.enableGeneratedDefaultStub)


class SerializationError(RuntimeException):
    """
    Indicates failure to serialize a uAPI Message.
    """

    def __init__(self, cause: Throwable) -> None:
        """
        Initialize SerializationError with the given cause.

        Args:
            cause (Throwable): The cause of the serialization error.
        """
        super().__init__(cause)


class SerializationImpl:
    """
    A serialization implementation that converts between pseudo-JSON Objects and
    byte array JSON payloads.

    Pseudo-JSON objects are defined as data structures that represent JSON
    objects as Maps and JSON arrays as Lists.
    """

    def toJson(self, message: Any) -> bytes:
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

    def toMsgPack(self, message: Any) -> bytes:
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

    def fromJson(self, bytes: bytes) -> Any:
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

    def fromMsgPack(self, bytes: bytes) -> Any:
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

    def __init__(self, serialization_impl: SerializationImpl, binary_encoder: _BinaryEncoder) -> None:
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
        return serialize(message, self.binary_encoder, self.serialization_impl)

    def deserialize(self, message_bytes: bytes) -> Message:
        """
        Deserialize a Message from a byte array.

        Args:
            message_bytes (bytes): The byte array containing the serialized message.

        Returns:
            Message: The deserialized message.
        """
        return deserialize(message_bytes, self.serialization_impl, self.binary_encoder)


class Server:
    """
    A uAPI Server.
    """

    class Options:
        """
        Options for the Server.
        """

        def __init__(self) -> None:
            self.on_error: Consumer[Throwable] = lambda e: None
            self.on_request: Consumer[Message] = lambda m: None
            self.on_response: Consumer[Message] = lambda m: None
            self.serializer: SerializationImpl = _DefaultSerializer()

    def __init__(self, u_api_schema: UApiSchema, handler: Callable[[Message], Message], options: Optional[Options] = None) -> None:
        if options is None:
            options = Server.Options()
        self.u_api_schema: UApiSchema = UApiSchema.extend(
            u_api_schema, getInternalUApiJson())
        self.handler: Callable[[Message], Message] = handler
        self.on_error: Consumer[Throwable] = options.on_error
        self.on_request: Consumer[Message] = options.on_request
        self.on_response: Consumer[Message] = options.on_response
        binary_encoding = constructBinaryEncoding(self.u_api_schema)
        binary_encoder = _ServerBinaryEncoder(binary_encoding)
        self.serializer: SerializationImpl = Serializer(
            options.serializer, binary_encoder)

    def process(self, request_message_bytes: bytes) -> bytes:
        """
        Process a given uAPI Request Message into a uAPI Response Message.

        Args:
            request_message_bytes (bytes): The request message bytes.

        Returns:
            bytes: The response message bytes.
        """
        return process_bytes(request_message_bytes, self.serializer, self.u_api_schema, self.on_error, self.on_request, self.on_response, self.handler)


class UApiError(RuntimeError):
    """
    Indicates critical failure in uAPI processing logic.
    """

    def __init__(self, message: str = None, cause: Throwable = None):
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

    def __init__(self, original: List[object], parsed: Dict[str, _UType], type_extensions: Dict[str, _UType]):
        self.original = original
        self.parsed = parsed
        self.type_extensions = type_extensions

    @staticmethod
    def from_json(json: str) -> 'UApiSchema':
        """
        Create a UApiSchema object from JSON.
        """
        return new_uapi_schema(json, {})

    @staticmethod
    def extend(base: 'UApiSchema', json: str) -> 'UApiSchema':
        """
        Extend a UApiSchema object with JSON.
        """
        return extend_uapi_schema(base, json, {})

    @staticmethod
    def from_json_with_extensions(json: str, type_extensions: Dict[str, _UType]) -> 'UApiSchema':
        """
        Create a UApiSchema object from JSON with type extensions.
        """
        return new_uapi_schema(json, type_extensions)

    @staticmethod
    def extend_with_extensions(base: 'UApiSchema', json: str, type_extensions: Dict[str, _UType]) -> 'UApiSchema':
        """
        Extend a UApiSchema object with JSON and type extensions.
        """
        return extend_uapi_schema(base, json, type_extensions)


class UApiSchemaParseError(RuntimeError):
    """
    Indicates failure to parse a uAPI Schema.
    """

    def __init__(self, schema_parse_failures: List[_SchemaParseFailure], cause: Exception = None):
        super().__init__(str(map_schema_parse_failures_to_pseudo_json(schema_parse_failures)))
        self.schema_parse_failures = schema_parse_failures
        self.schema_parse_failures_pseudo_json = map_schema_parse_failures_to_pseudo_json(
            schema_parse_failures)

    @staticmethod
    def map_schema_parse_failures_to_pseudo_json(schema_parse_failures: List[_SchemaParseFailure]) -> List[Dict[str, Any]]:
        """
        Map schema parse failures to pseudo JSON format.
        """
        return [{'path': f.path, 'reason': {f.reason: f.data}} for f in schema_parse_failures]
