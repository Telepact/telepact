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


FunctionRoute = Callable[[str, 'Message'], Awaitable['Message']]


class FunctionRouter:
    def __init__(self, function_routes: dict[str, FunctionRoute] | None = None) -> None:
        self.function_routes: dict[str, FunctionRoute] = dict(function_routes or {})

    async def route(self, request_message: 'Message') -> 'Message':
        function_name = request_message.get_body_target()
        function_route = self.function_routes.get(function_name)
        if function_route is None:
            raise RuntimeError(f"Unknown function: {function_name}")
        return await function_route(function_name, request_message)
