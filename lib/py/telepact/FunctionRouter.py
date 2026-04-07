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

from typing import Awaitable, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .Message import Message


ServerFunction = Callable[[dict[str, object], dict[str, object]], Awaitable['Message']]
ServerMiddleware = Callable[['Message', 'FunctionRouter'], Awaitable['Message']]


class FunctionRouter:
    def __init__(self) -> None:
        self._functions: dict[str, tuple[bool, ServerFunction]] = {}

    def register(self, function_name: str, handler: ServerFunction) -> 'FunctionRouter':
        return self.register_unauthenticated(function_name, handler)

    def register_unauthenticated(self, function_name: str, handler: ServerFunction) -> 'FunctionRouter':
        self._functions[function_name] = (False, handler)
        return self

    def register_authenticated(self, function_name: str, handler: ServerFunction) -> 'FunctionRouter':
        self._functions[function_name] = (True, handler)
        return self

    async def route(self, request_message: 'Message') -> 'Message':
        from .Message import Message

        function_name = request_message.get_body_target()
        arguments = request_message.get_body_payload()
        registration = self._functions.get(function_name)
        if registration is None:
            raise RuntimeError(f"Unknown function: {function_name}")
        authenticated, handler = registration
        if authenticated:
            auth_result = request_message.headers.get('@result')
            if auth_result is not None:
                return Message({}, cast(dict[str, object], auth_result))
            if '@auth_' not in request_message.headers:
                return Message({}, {'ErrorUnauthenticated_': {'message!': 'Valid authentication is required.'}})
        return await handler(request_message.headers, arguments)
