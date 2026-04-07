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
ServerNext = Callable[[dict[str, object], str, dict[str, object]], Awaitable['Message']]
ServerMiddleware = Callable[[dict[str, object], str, dict[str, object], ServerNext], Awaitable['Message']]


class FunctionRouter:
    def __init__(self) -> None:
        self._functions: dict[str, ServerFunction] = {}

    def register(self, function_name: str, handler: ServerFunction) -> 'FunctionRouter':
        self._functions[function_name] = handler
        return self

    async def middleware(
        self,
        headers: dict[str, object],
        function_name: str,
        arguments: dict[str, object],
        next: ServerNext,
    ) -> 'Message':
        handler = self._functions.get(function_name)
        if handler is not None:
            return await handler(headers, arguments)
        return await next(headers, function_name, arguments)
