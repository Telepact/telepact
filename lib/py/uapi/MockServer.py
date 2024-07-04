from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from uapi.Message import Message
    from uapi.UApiSchema import UApiSchema
    from uapi.internal.mock.MockInvocation import MockInvocation
    from uapi.internal.mock.MockStub import MockStub


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

    def __init__(self, u_api_schema: 'UApiSchema', options: Options) -> None:
        from uapi.internal.schema.ExtendUApiSchema import extend_uapi_schema
        from uapi.internal.schema.GetMockUApiJson import get_mock_uapi_json
        from uapi.Server import Server
        from uapi.RandomGenerator import RandomGenerator

        self.random: RandomGenerator = RandomGenerator(
            options.generated_collection_length_min, options.generated_collection_length_max)
        self.enableGeneratedDefaultStub: bool = options.enable_message_response_generation
        self.enable_optional_field_generation: bool = options.enable_optional_field_generation
        self.randomize_optional_field_generation: bool = options.randomize_optional_field_generation

        self.stubs: list[MockStub] = []
        self.invocations: list[MockInvocation] = []

        combined_u_api_schema: UApiSchema = extend_uapi_schema(
            u_api_schema, get_mock_uapi_json())

        server_options = Server.Options()
        server_options.on_error = options.on_error
        server_options.auth_required = False

        self.server = Server(
            combined_u_api_schema, self._handle, server_options)

    async def process(self, message: bytes) -> bytes:
        """
        Process a given uAPI Request Message into a uAPI Response Message.

        :param message: The uAPI request message.
        :return: The uAPI response message.
        """
        return await self.server.process(message)

    async def _handle(self, request_message: 'Message') -> 'Message':
        from uapi.internal.mock.MockHandle import mock_handle
        return await mock_handle(request_message, self.stubs, self.invocations, self.random,
                                 self.server.u_api_schema, self.enableGeneratedDefaultStub,
                                 self.enable_optional_field_generation, self.randomize_optional_field_generation)
