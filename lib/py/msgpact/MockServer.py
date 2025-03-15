from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .Message import Message
    from .MockMsgPactSchema import MockMsgPactSchema
    from .internal.mock.MockInvocation import MockInvocation
    from .internal.mock.MockStub import MockStub


class MockServer:
    """
    A Mock instance of a msgPact server.
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

    def __init__(self, mock_msgpact_schema: 'MockMsgPactSchema', options: Options) -> None:
        from .Server import Server
        from .RandomGenerator import RandomGenerator
        from .MsgPactSchema import MsgPactSchema

        self.random: RandomGenerator = RandomGenerator(
            options.generated_collection_length_min, options.generated_collection_length_max)
        self.enableGeneratedDefaultStub: bool = options.enable_message_response_generation
        self.enable_optional_field_generation: bool = options.enable_optional_field_generation
        self.randomize_optional_field_generation: bool = options.randomize_optional_field_generation

        self.stubs: list[MockStub] = []
        self.invocations: list[MockInvocation] = []

        server_options = Server.Options()
        server_options.on_error = options.on_error
        server_options.auth_required = False

        msgpact_schema = MsgPactSchema(mock_msgpact_schema.original, mock_msgpact_schema.parsed,
                                       mock_msgpact_schema.parsed_request_headers, mock_msgpact_schema.parsed_response_headers)

        self.server = Server(
            msgpact_schema, self._handle, server_options)

    async def process(self, message: bytes) -> bytes:
        """
        Process a given msgPact Request Message into a msgPact Response Message.

        :param message: The msgPact request message.
        :return: The msgPact response message.
        """
        return await self.server.process(message)

    async def _handle(self, request_message: 'Message') -> 'Message':
        from .internal.mock.MockHandle import mock_handle
        return await mock_handle(request_message, self.stubs, self.invocations, self.random,
                                 self.server.u_api_schema, self.enableGeneratedDefaultStub,
                                 self.enable_optional_field_generation, self.randomize_optional_field_generation)
