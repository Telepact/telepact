from typing import Callable, Dict, List, Any
from uapi.internal.mock import MockInvocation, MockStub
from uapi.internal.types import UMockCall, UMockStub, UType
from uapi.internal.schema import extend_uapi_schema, get_mock_uapi_json
from uapi import Server, UApiSchema, RandomGenerator, Message


class Options:
    def __init__(self):
        self.on_error: Callable[[Exception], None] = lambda e: None
        self.enable_message_response_generation: bool = True
        self.enable_optional_field_generation: bool = True
        self.randomize_optional_field_generation: bool = True
        self.generated_collection_length_min: int = 0
        self.generated_collection_length_max: int = 3


class MockServer:
    def __init__(self, uapi_schema: UApiSchema, options: Options):
        self.random = RandomGenerator(
            options.generated_collection_length_min, options.generated_collection_length_max)
        self.enable_generated_default_stub = options.enable_message_response_generation
        self.enable_optional_field_generation = options.enable_optional_field_generation
        self.randomize_optional_field_generation = options.randomize_optional_field_generation

        parsed_types: Dict[str, UType] = {}
        type_extensions: Dict[str, UType] = {
            "_ext.Call_": UMockCall(parsed_types),
            "_ext.Stub_": UMockStub(parsed_types)
        }

        combined_uapi_schema = extend_uapi_schema(
            uapi_schema, get_mock_uapi_json(), type_extensions)

        server_options = Server.Options()
        server_options.on_error = options.on_error
        server_options.auth_required = False

        self.server = Server(combined_uapi_schema, self.handle, server_options)

        final_uapi_schema = self.server.uapi_schema
        final_parsed_uapi_schema = final_uapi_schema.parsed

        parsed_types.update(final_parsed_uapi_schema)

        self.stubs: List[MockStub] = []
        self.invocations: List[MockInvocation] = []

    def process(self, message: bytes) -> bytes:
        return self.server.process(message)

    def handle(self, request_message: Message) -> Message:
        return mock_handle(request_message, self.stubs, self.invocations, self.random,
                           self.server.uapi_schema, self.enable_generated_default_stub, self.enable_optional_field_generation,
                           self.randomize_optional_field_generation)
