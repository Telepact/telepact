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

from typing import Callable, TYPE_CHECKING, Awaitable

from ..Message import Message

if TYPE_CHECKING:
    from ..Serializer import Serializer
    from ..TelepactSchema import TelepactSchema


async def process_bytes(request_message_bytes: bytes, serializer: 'Serializer', telepact_schema: 'TelepactSchema',
                        on_error: Callable[[Exception], None], on_request: Callable[['Message'], None],
                        on_response: Callable[['Message'], None], handler: Callable[['Message'], Awaitable['Message']]) -> bytes:
    from ..internal.HandleMessage import handle_message
    from ..internal.ParseRequestMessage import parse_request_message

    try:
        request_message = parse_request_message(
            request_message_bytes, serializer, telepact_schema, on_error)

        try:
            on_request(request_message)
        except Exception:
            pass

        response_message = await handle_message(
            request_message, telepact_schema, handler, on_error)

        try:
            on_response(response_message)
        except Exception:
            pass

        return serializer.serialize(response_message)
    except Exception as e:
        try:
            on_error(e)
        except Exception:
            pass

        return serializer.serialize(Message({}, {"ErrorUnknown_": {}}))
