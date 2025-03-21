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

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .Message import Message
    from .MockTelepactSchema import MockTelepactSchema
    from .internal.mock.MockInvocation import MockInvocation
    from .internal.mock.MockStub import MockStub


class MockServer:
    """
    A Mock instance of a telepact server.
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

    def __init__(self, mock_telepact_schema: 'MockTelepactSchema', options: Options) -> None:
        from .Server import Server
        from .RandomGenerator import RandomGenerator
        from .TelepactSchema import TelepactSchema

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

        telepact_schema = TelepactSchema(mock_telepact_schema.original, mock_telepact_schema.parsed,
                                       mock_telepact_schema.parsed_request_headers, mock_telepact_schema.parsed_response_headers)

        self.server = Server(
            telepact_schema, self._handle, server_options)

    async def process(self, message: bytes) -> bytes:
        """
        Process a given telepact Request Message into a telepact Response Message.

        :param message: The telepact request message.
        :return: The telepact response message.
        """
        return await self.server.process(message)

    async def _handle(self, request_message: 'Message') -> 'Message':
        from .internal.mock.MockHandle import mock_handle
        return await mock_handle(request_message, self.stubs, self.invocations, self.random,
                                 self.server.telepact_schema, self.enableGeneratedDefaultStub,
                                 self.enable_optional_field_generation, self.randomize_optional_field_generation)
