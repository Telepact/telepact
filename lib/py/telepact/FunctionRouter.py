#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
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
