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
from ..SerializationError import SerializationError
from ..TelepactError import TelepactError
from ..internal.UnknownError import build_unknown_error_message

if TYPE_CHECKING:
    from ..Serializer import Serializer
    from ..Server import Middleware, FunctionRouter, UpdateHeaders
    from ..TelepactSchema import TelepactSchema
    from ..Response import Response


async def process_bytes(request_message_bytes: bytes, update_headers: 'UpdateHeaders | None',
                         serializer: 'Serializer', telepact_schema: 'TelepactSchema',
                         on_error: Callable[[Exception], None], on_request: Callable[['Message'], None],
                         on_response: Callable[['Message'], None], on_auth: Callable[[dict[str, object]], dict[str, object]],
                         middleware: 'Middleware', function_router: 'FunctionRouter') -> 'Response':
    from ..internal.HandleMessage import handle_message
    from ..internal.ParseRequestMessage import parse_request_message
    from ..Response import Response

    try:
        request_message = parse_request_message(
            request_message_bytes, serializer, telepact_schema, on_error)

        try:
            on_request(request_message)
        except Exception:
            pass

        response_message = await handle_message(
            request_message, update_headers, telepact_schema, middleware, function_router, on_error, on_auth)

        try:
            on_response(response_message)
        except Exception:
            pass

        try:
            response_bytes = serializer.serialize(response_message)
        except Exception as e:
            wrapped = (
                TelepactError(
                    "telepact response serialization failed",
                    kind="serialization",
                    cause=e,
                )
                if isinstance(e, SerializationError)
                else TelepactError(
                    "telepact server processing failed while serializing the response",
                    kind="serialization",
                    cause=e,
                )
            )
            try:
                on_error(wrapped)
            except Exception:
                pass
            response_bytes = serializer.serialize(build_unknown_error_message(wrapped))
            return Response(response_bytes, {})

        return Response(response_bytes, response_message.headers)
    except Exception as e:
        wrapped = e if isinstance(e, TelepactError) else TelepactError(
            "telepact server processing failed",
            cause=e,
        )
        try:
            on_error(wrapped)
        except Exception:
            pass

        response_bytes = serializer.serialize(build_unknown_error_message(wrapped))

        return Response(response_bytes, {})
