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
        from .FunctionRouter import FunctionRouter
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

        telepact_schema = TelepactSchema(mock_telepact_schema.original, mock_telepact_schema.full, mock_telepact_schema.parsed,
                                         mock_telepact_schema.parsed_request_headers, mock_telepact_schema.parsed_response_headers)
        function_router = FunctionRouter(self._create_function_routes(telepact_schema))

        self.server = Server(
            telepact_schema, function_router, server_options)

    async def process(self, message: bytes) -> bytes:
        """
        Process a given telepact Request Message into a telepact Response Message.

        :param message: The telepact request message.
        :return: The telepact response message.
        """
        return await self.server.process(message)

    def _create_function_routes(self, telepact_schema: 'TelepactSchema') -> dict[str, object]:
        from .internal.mock.MockHandle import (
            handle_auto_mock_function,
            handle_clear_calls,
            handle_clear_stubs,
            handle_create_stub,
            handle_set_random_seed,
            handle_verify,
            handle_verify_no_more_interactions,
        )

        function_routes = {
            function_name: (
                lambda _function_name, request_message, self=self, telepact_schema=telepact_schema:
                    handle_auto_mock_function(
                        request_message,
                        self.stubs,
                        self.invocations,
                        self.random,
                        telepact_schema,
                        self.enableGeneratedDefaultStub,
                        self.enable_optional_field_generation,
                        self.randomize_optional_field_generation,
                    )
            )
            for function_name in telepact_schema.parsed.keys()
            if _is_auto_mock_function_name(function_name)
        }

        function_routes["fn.createStub_"] = lambda _function_name, request_message, self=self: handle_create_stub(
            request_message,
            self.stubs,
        )
        function_routes["fn.verify_"] = lambda _function_name, request_message, self=self: handle_verify(
            request_message,
            self.invocations,
        )
        function_routes["fn.verifyNoMoreInteractions_"] = lambda _function_name, _request_message, self=self: handle_verify_no_more_interactions(
            self.invocations,
        )
        function_routes["fn.clearCalls_"] = lambda _function_name, _request_message, self=self: handle_clear_calls(
            self.invocations,
        )
        function_routes["fn.clearStubs_"] = lambda _function_name, _request_message, self=self: handle_clear_stubs(
            self.stubs,
        )
        function_routes["fn.setRandomSeed_"] = lambda _function_name, request_message, self=self: handle_set_random_seed(
            request_message,
            self.random,
        )
        return function_routes


def _is_auto_mock_function_name(function_name: str) -> bool:
    return function_name.startswith("fn.") and not function_name.endswith(".->") and not function_name.endswith("_")
