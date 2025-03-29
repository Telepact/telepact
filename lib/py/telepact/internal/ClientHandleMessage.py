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

import asyncio
from typing import Callable, TYPE_CHECKING, cast, Awaitable

if TYPE_CHECKING:
    from ..Message import Message
    from ..Serializer import Serializer


async def client_handle_message(request_message: 'Message',
                                 adapter: Callable[['Message', 'Serializer'], Awaitable['Message']],
                                 serializer: 'Serializer',
                                 timeout_ms_default: int,
                                 use_binary_default: bool,
                                 always_send_json: bool) -> 'Message':
    from ..TelepactError import TelepactError

    header: dict[str, object] = request_message.headers

    try:
        if "@time_" not in header:
            header["@time_"] = timeout_ms_default

        if use_binary_default:
            header["@binary_"] = True

        if header.get('@binary_', False) and always_send_json:
            header["_forceSendJson"] = True

        timeout_ms = cast(int, header.get("@time_"))

        async with asyncio.timeout(timeout_ms / 1000):
            response_message = await adapter(request_message, serializer)

        if response_message.body == {"ErrorParseFailure_": {"reasons": [{"IncompatibleBinaryEncoding": {}}]}}:
            header["@binary_"] = True
            header["_forceSendJson"] = True

            async with asyncio.timeout(timeout_ms / 1000):
                return await adapter(request_message, serializer)

        return response_message
    except Exception as e:
        raise TelepactError() from e
